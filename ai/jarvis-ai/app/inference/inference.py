from models.model_loader import get_model
from engine.logger import log_inference_error

from inference.runtime_object import RUNTIME_ACCESS

from inference.events import *
from inference.tools.tool_registry import *
from inference.queue_system import *
from inference.runtime_state import (
    set_model_warm,
    set_request_status,
    add_request_history
)

from inference.runtime_errors import add_error
from inference.runtime_errors import inc_error_retry
from inference.runtime_errors import get_error_retry_count

from config.runtime_config import DEFAULT_SYSTEM_PROMPT
from config.runtime_config import (
    MAX_REQUEST_HISTORY,
    MAX_REQUESTS_PER_WINDOW,
    RATE_WINDOW,
    LLM_TIMEOUT,
    LLM_MAX_TOKENS,
    LLM_TEMP
)

import time
import concurrent.futures
import threading
import uuid


# LOCKS

BUSY_LOCK = threading.Lock()
HISTORY_LOCK = threading.Lock()
STATE_LOCK = threading.Lock()


# STATUS

STATUS_QUEUED = "queued"
STATUS_PROCESSING = "processing"
STATUS_FINISHED = "finished"
STATUS_ERROR = "error"
STATUS_TIMEOUT = "timeout"
STATUS_CANCELLED = "cancelled"


ALLOWED_TRANSITIONS = {

    None:[STATUS_QUEUED,STATUS_PROCESSING],

    STATUS_QUEUED:[
        STATUS_PROCESSING,
        STATUS_CANCELLED
    ],

    STATUS_PROCESSING:[
        STATUS_FINISHED,
        STATUS_ERROR,
        STATUS_TIMEOUT,
        STATUS_CANCELLED
    ],

    STATUS_FINISHED:[],
    STATUS_ERROR:[],
    STATUS_TIMEOUT:[],
    STATUS_CANCELLED:[]
}


# EVENTS

EVENT_REQUEST_STARTED = "request_started"
EVENT_REQUEST_FINISHED = "request_finished"
EVENT_REQUEST_CANCELLED = "request_cancelled"
EVENT_REQUEST_FAILED = "request_failed"
EVENT_REQUEST_TIMEOUT = "request_timeout"

EVENT_TOOL_CALLED = "tool_called"
EVENT_REQUEST_QUEUED = "request_queued"
EVENT_REQUEST_RETRY = "request_retry"
EVENT_REQUEST_ROUTED = "request_routed"


# ERRORS

ERROR_MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
ERROR_TIMEOUT = "INFERENCE_TIMEOUT"
ERROR_BUSY = "MODEL_BUSY"
ERROR_UNKNOWN = "UNKNOWN_ERROR"

ERROR_MODEL = "MODEL_ERROR"
ERROR_RUNTIME = "RUNTIME_ERROR"
ERROR_TOOL = "TOOL_ERROR"
ERROR_VALIDATION = "VALIDATION_ERROR"

ERROR_CLASS_MAP = {

    ERROR_MODEL_NOT_LOADED: ERROR_MODEL,

    ERROR_BUSY: ERROR_MODEL,

    ERROR_TIMEOUT: ERROR_RUNTIME,

    ERROR_UNKNOWN: ERROR_RUNTIME

}

ERROR_RETRY_MAP = {

    ERROR_MODEL: True,

    ERROR_RUNTIME: False,

    ERROR_TOOL: False,

    ERROR_VALIDATION: False

}

def can_retry_error(error_class):

    if error_class not in ERROR_MAX_RETRIES:

        return False

    from inference.runtime_state import get_error_retry_count

    retries = get_error_retry_count(error_class)

    max_retries = ERROR_MAX_RETRIES.get(error_class,0)

    return retries < max_retries

def get_retry_reason(error_class):

    from inference.runtime_state import get_error_retry_count

    retries = get_error_retry_count(error_class)

    max_retries = ERROR_MAX_RETRIES.get(error_class,0)

    if error_class not in ERROR_RETRY_MAP:

        return "unknown_error"

    if not ERROR_RETRY_MAP.get(error_class):

        return "retry_not_allowed"

    if retries >= max_retries:

        return "max_retries_reached"

    return "retry_available"


ERROR_MAX_RETRIES = {

    ERROR_MODEL: 2,

    ERROR_RUNTIME: 0,

    ERROR_TOOL: 0,

    ERROR_VALIDATION: 0

}

ERROR_SEVERITY = {

    ERROR_MODEL: "medium",

    ERROR_RUNTIME: "high",

    ERROR_TOOL: "medium",

    ERROR_VALIDATION: "low"

}


# REQUEST CLASSIFICATION

def classify_request(prompt):

    if not prompt:
        return "inference"

    text = prompt.lower().strip()

    if text.startswith("tool:"):
        return "tool"

    return "inference"


def decide_execution_path(prompt):

    route = classify_request(prompt)

    if route == "tool":
        return "tool"

    return "ai"


def parse_tool_command(prompt):

    if not prompt:
        return None,{}

    text = prompt.strip()

    if not text.startswith("tool:"):
        return None,{}

    command = text[5:].strip()

    if not command:
        return None,{}

    parts = command.split()

    tool_name = parts[0]

    args = {}

    for part in parts[1:]:

        if "=" in part:

            key,value = part.split("=",1)

            args[key.strip()] = value.strip()

    return tool_name,args


def execute_routed_request(route,prompt,request_id):

    if route == "status":

        return {

            "error":False,
            "route":"status",
            "data":inference_status()

        }

    if route == "memory":

        return {

            "error":False,
            "route":"memory",
            "message":"memory not implemented yet"

        }

    if route == "tool":

        tool_name,args = parse_tool_command(prompt)

        if not tool_name:

            return {

                "error":True,
                "message":"tool name missing"

            }

        result = execute_tool(tool_name,args)

        return {

            "error":False,
            "route":"tool",
            "data":result

        }

    return None


# REQUEST FINALIZE

def finalize_request(
    request_id,
    status,
    duration,
    tokens=0,
    tokens_per_sec=0,
    error=None,
    prompt=None
):

    global LAST_DURATION
    global LAST_TOKENS
    global TOKENS_PER_SEC
    global LAST_SUCCESS_REQUEST
    global LAST_SUCCESS_TIME
    global LAST_CRASH_TIME
    global LAST_CRASH_REQUEST

    set_request_status(request_id,status)


    if status == STATUS_FINISHED:

        RUNTIME_ACCESS.metric_inc("requests_success")

        RUNTIME_ACCESS.add_history({

            "request_id":request_id,

            "status":"finished",

            "duration":duration,

            "tokens":tokens,

            "tokens_per_sec":tokens_per_sec,

            "error":None

        })

        LAST_SUCCESS_REQUEST = request_id
        LAST_SUCCESS_TIME = time.time()

        RUNTIME_ACCESS.emit_event(
            "request_finished",
            {
                "request_id":request_id,
                "status":status,
                "duration":duration
            }
        )

        RUNTIME_ACCESS.metric_set("last_success_request",request_id)


    elif status == STATUS_TIMEOUT:

        LAST_CRASH_TIME = time.time()
        LAST_CRASH_REQUEST = request_id

        track_error(request_id,ERROR_TIMEOUT)

        RUNTIME_ACCESS.metric_inc("requests_error")
        RUNTIME_ACCESS.metric_inc("requests_timeout")

        add_error(ERROR_RUNTIME, request_id)

        error_class = ERROR_RUNTIME

        inc_error_retry(error_class)

        add_error(error_class, request_id)

        RUNTIME_ACCESS.emit_event(
            "request_timeout",
            {"request_id":request_id}
        )


    elif status == STATUS_ERROR:

        LAST_CRASH_TIME = time.time()
        LAST_CRASH_REQUEST = request_id

        track_error(request_id,error)

        RUNTIME_ACCESS.metric_inc("requests_error")

        error_class = ERROR_CLASS_MAP.get(error, ERROR_RUNTIME)

        inc_error_retry(error_class)        

        add_error(error_class, request_id)

        retryable = ERROR_RETRY_MAP.get(error_class, False)

        severity = ERROR_SEVERITY.get(error_class,"medium")

        max_retries = ERROR_MAX_RETRIES.get(error_class,0)

        retry_allowed = can_retry_error(error_class)

        retry_reason = get_retry_reason(error_class)

        RUNTIME_ACCESS.emit_event(

            "request_failed",

            {

                "request_id":request_id,

                "error_class":error_class,

                "retry_reason": retry_reason,

                "retryable":retryable,

                "retry_allowed":retry_allowed,

                "severity":severity,

                "max_retries":max_retries

            }

        )


    LAST_DURATION = duration
    LAST_TOKENS = tokens
    TOKENS_PER_SEC = tokens_per_sec


    RUNTIME_ACCESS.metric_set("tokens_per_sec",tokens_per_sec)
    RUNTIME_ACCESS.metric_set("tokens_last",tokens)
    RUNTIME_ACCESS.metric_set("last_duration", duration)


    total = RUNTIME_ACCESS.metric_get("total_duration") or 0

    total += duration

    RUNTIME_ACCESS.metric_set("total_duration", total)


    count = RUNTIME_ACCESS.metric_get("requests_success") or 0

    if count > 0:

        RUNTIME_ACCESS.metric_set(
            "avg_duration",
            total / count
        )


    add_request_history(

        request_id,
        status,
        duration,
        tokens,
        tokens_per_sec,
        error,
        prompt

    )

    RUNTIME_ACCESS.write("last_request", {
        "request_id": request_id,
        "status": status,
        "duration": duration,
        "tokens": tokens,
        "tokens_per_sec": tokens_per_sec
    })


# ENTRY POINT

def run_inference(
    prompt,
    max_tokens=LLM_MAX_TOKENS,
    temperature=LLM_TEMP,
    request_id=None,
    priority=False
):

    print("RUN_INFERENCE CALLED:", prompt)

    start = time.time()

    tokens = 0
    tokens_per_sec = 0

    model = get_model()

    if not model:

        finalize_request(
            request_id,
            STATUS_ERROR,
            0,
            error=ERROR_MODEL_NOT_LOADED,
            prompt=prompt
        )

        return


    route = decide_execution_path(prompt)

    routed = execute_routed_request(route,prompt,request_id)

    if routed:

        finalize_request(
            request_id,
            STATUS_FINISHED,
            time.time()-start,
            prompt=prompt
        )

        return routed


    result = model(

        prompt,
        max_tokens=max_tokens,
        temperature=temperature

    )

    print("AFTER MODEL CALL")

    duration = time.time() - start


    if isinstance(result, dict):

        tokens = (
            result.get("tokens")
            or result.get("completion_tokens")
            or result.get("generated_tokens")
            or max_tokens
        )

    elif isinstance(result, str):

        tokens = max_tokens


    if duration > 0 and tokens > 0:

        tokens_per_sec = tokens / duration


    print("MODEL RESULT:", result)
    print("TOKENS DEBUG:", tokens)
    print("TPS DEBUG:", tokens_per_sec)


    finalize_request(

        request_id,
        STATUS_FINISHED,
        duration,
        tokens,
        tokens_per_sec,
        prompt=prompt

    )


    return result
