from inference.runtime_object import get_runtime

from inference.runtime_errors import get_last_error
from inference.runtime_errors import get_error_types
from inference.runtime_errors import get_error_history

import time


LAST_STATE_CHANGE = time.time()

REQUEST_STATUS = {}
CANCELLED_REQUESTS = set()
REQUEST_HISTORY = []
REQUEST_TIMESTAMPS = []

MAX_EVENT_HISTORY = 100
RUNTIME_EVENTS = []


def add_runtime_event(event_type, data=None):

    entry = {
        "type": event_type,
        "time": time.time(),
        "data": data or {}
    }

    if len(RUNTIME_EVENTS) >= MAX_EVENT_HISTORY:
        RUNTIME_EVENTS.pop(0)

    RUNTIME_EVENTS.append(entry)


def get_runtime_events():
    return RUNTIME_EVENTS


MODEL_WARM = False
get_runtime().model_warm = MODEL_WARM

JARVIS_START_TIME = time.time()

EVENT_LISTENERS = {}

CURRENT_HEALTH = "unknown"
LAST_HEALTH = "unknown"
LAST_HEALTH_CHANGE = None


def get_current_health():
    return get_runtime().health


def get_last_health():
    return LAST_HEALTH


def get_last_health_change():
    return LAST_HEALTH_CHANGE


def update_health(new_health):

    global CURRENT_HEALTH, LAST_HEALTH, LAST_HEALTH_CHANGE

    if CURRENT_HEALTH == new_health:
        return False

    LAST_HEALTH = CURRENT_HEALTH
    CURRENT_HEALTH = new_health

    get_runtime().health = new_health

    LAST_HEALTH_CHANGE = time.time()
    return True


def is_busy():
    return get_runtime().busy


def get_busy_state():
    return get_runtime().busy


def get_current_request():
    return get_runtime().current_request


def get_last_state_change():
    return LAST_STATE_CHANGE


def get_request_count():
    return len(REQUEST_STATUS)


def get_queue_health():
    return {
        "busy": get_runtime().busy,
        "current": get_runtime().current_request
    }


def get_request_status(request_id):
    return REQUEST_STATUS.get(request_id)


def get_all_request_status():
    return REQUEST_STATUS


def is_request_cancelled(request_id):
    return request_id in CANCELLED_REQUESTS


def get_cancelled_requests():
    return CANCELLED_REQUESTS


def get_request_history():
    return REQUEST_HISTORY


def get_request_timestamps():
    return REQUEST_TIMESTAMPS


def get_last_requests(limit=50):

    if limit <= 0:
        return []

    return REQUEST_HISTORY[-limit:]


def is_model_warm():
    return MODEL_WARM


def get_start_time():
    return JARVIS_START_TIME


def get_uptime():
    return int(time.time() - get_runtime().start_time)


def get_event_listeners():
    return EVENT_LISTENERS


def has_event_listeners():
    return len(EVENT_LISTENERS) > 0


def get_listener(event):
    return EVENT_LISTENERS.get(event)


def get_runtime_snapshot():

    rt = get_runtime()

    return {
        "state": rt.state,
        "last_state_change": LAST_STATE_CHANGE,
        "busy": rt.busy,
        "current_request": rt.current_request,
        "model_warm": rt.model_warm,
        "health": rt.health,
        "last_health": LAST_HEALTH,
        "last_health_change": LAST_HEALTH_CHANGE,
        "total_requests": len(REQUEST_STATUS),
        "cancelled_requests": len(CANCELLED_REQUESTS),
        "history_size": len(REQUEST_HISTORY),
        "uptime": int(time.time() - rt.start_time)
    }


def set_busy(value):
    get_runtime().busy = value


def set_current_request(request_id):
    get_runtime().current_request = request_id


def clear_current_request():
    get_runtime().current_request = None


def set_model_warm(value):

    global MODEL_WARM

    MODEL_WARM = value
    get_runtime().model_warm = value


def get_model_warm():
    return get_runtime().model_warm


def set_request_status(request_id, status):

    REQUEST_STATUS[request_id] = {
        "status": status,
        "updated": time.time()
    }


def add_request_history(
    request_id,
    status,
    duration,
    tokens=0,
    tokens_per_sec=0,
    error=None,
    prompt=None
):

    REQUEST_HISTORY.append({
        "request_id": request_id,
        "status": status,
        "duration": duration,
        "tokens": tokens,
        "tokens_per_sec": tokens_per_sec,
        "error": error,
        "prompt": prompt,
        "time": time.time()
    })

    if len(REQUEST_HISTORY) > 100:
        REQUEST_HISTORY.pop(0)


def get_worker_heartbeat_age():
    rt = get_runtime()
    return time.time() - rt.worker_heartbeat


def get_worker_last_activity_age():
    rt = get_runtime()
    return time.time() - rt.worker_last_activity


def get_worker_status():
    return get_runtime().worker_status
