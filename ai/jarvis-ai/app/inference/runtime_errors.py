from error.error_classifier import ErrorClassifier

import time

from threading import Lock


classifier = ErrorClassifier()

MAX_ERROR_HISTORY = 50

ERROR_HISTORY = []

ERROR_TYPES = {}

ERROR_LOCK = Lock()

ERROR_RETRY_COUNT = {}

LAST_ERROR_TYPE = None

LAST_ERROR_SPIKE_EVENT = 0

ERROR_SPIKE_COOLDOWN = 60

ERROR_SEVERITY = {

    "TimeoutError":"warning",

    "ModelError":"critical",

    "GPUError":"critical",

    "QueueError":"warning",

    "UNKNOWN_ERROR":"info"

}


def get_error_severity(error_type):

    return ERROR_SEVERITY.get(error_type,"warning")


def add_error(error_type, request_id=None):

    if not error_type:

        error_type = "UNKNOWN_ERROR"

    global LAST_ERROR_TYPE

    classification = classifier.classify(error_type)

    entry = {

        "type": error_type,

        "severity": get_error_severity(error_type),

        "category": classification["category"],

        "retry_policy": classification["retry_policy"],

        "request_id": request_id,

        "time": time.time(),

        "count": ERROR_TYPES.get(error_type,0)+1

    }

    with ERROR_LOCK:

        if len(ERROR_HISTORY) >= MAX_ERROR_HISTORY:

            ERROR_HISTORY.pop(0)

        ERROR_HISTORY.append(entry)

    if entry["severity"] == "critical":

        from inference.runtime_state import add_runtime_event

        add_runtime_event(

            "critical_error",

            {

                "type":error_type,

                "request_id":request_id

            }

        )

    LAST_ERROR_TYPE = error_type

    with ERROR_LOCK:

        ERROR_TYPES[error_type] = ERROR_TYPES.get(error_type,0) + 1

    if is_error_spiking():

        recent_types = get_recent_error_types()

        now = time.time()

        global LAST_ERROR_SPIKE_EVENT

        if now - LAST_ERROR_SPIKE_EVENT > ERROR_SPIKE_COOLDOWN:

            from inference.runtime_state import add_runtime_event

            add_runtime_event(

                "error_spike",

                {

                    "type":error_type,

                    "recent_errors":get_recent_error_count(60),

                    "pattern":get_recent_error_types()

                }

            )

            LAST_ERROR_SPIKE_EVENT = now


def get_last_error():

    return LAST_ERROR_TYPE


def get_error_types():

    return ERROR_TYPES


def get_error_history():

    return ERROR_HISTORY


def inc_error_retry(error_type):

    ERROR_RETRY_COUNT[error_type] = ERROR_RETRY_COUNT.get(error_type,0) + 1


def get_error_retry_count(error_type):

    return ERROR_RETRY_COUNT.get(error_type,0)


def get_most_common_error():

    if not ERROR_TYPES:
        return None

    return max(ERROR_TYPES, key=ERROR_TYPES.get)


def get_recent_error_count(seconds=60):

    now = time.time()

    count = 0

    for e in ERROR_HISTORY:

        if now - e["time"] <= seconds:

            count += 1

    return count


def is_error_spiking(seconds=60, threshold=3):

    recent_types = get_recent_error_types(seconds)

    for error_type, count in recent_types.items():

        if count >= threshold:

            return True

    return False


def get_recent_error_types(seconds=60):

    now = time.time()

    types = {}

    for e in ERROR_HISTORY:

        if now - e["time"] <= seconds:

            t = e["type"]

            types[t] = types.get(t,0) + 1

    return types
