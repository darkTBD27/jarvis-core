import time

from inference.runtime_state import *
from inference.metrics import *


def subscribe_event(event_name,callback):

    if event_name not in EVENT_LISTENERS:

        EVENT_LISTENERS[event_name]=[]

    EVENT_LISTENERS[event_name].append(callback)


def emit_event(event_name,data=None):

    listeners = EVENT_LISTENERS.get(event_name,[])

    for callback in listeners.copy():

        try:
            callback(data,event_name)
        except Exception:
            pass


def debug_event(data,event_type):

    if not data:
        return

    rid=data.get("request_id","unknown")

    print(f"[EVENT] {event_type} request={rid}")


def track_last_event(data,event_type):

    global LAST_EVENT
    global LAST_EVENT_TIME

    LAST_EVENT = event_type
    LAST_EVENT_TIME = time.time()


def track_jarvis_state(data,event):

    global JARVIS_STATE

    if event == "request_started":
        JARVIS_STATE = "thinking"

    elif event == "request_queued":
        JARVIS_STATE = "queued"

    elif event == "request_finished":
        JARVIS_STATE = "idle"

    elif event == "request_failed":
        JARVIS_STATE = "error"

    elif event == "request_timeout":
        JARVIS_STATE = "timeout"

    elif event == "tool_called":
        JARVIS_STATE = "tool"

    elif event == "request_cancelled":
        JARVIS_STATE = "idle"


def track_tool_usage(data,event):

    global LAST_TOOL_USED
    global LAST_TOOL_TIME
    global LAST_TOOL_ARGS

    LAST_TOOL_USED = data.get("tool")
    LAST_TOOL_ARGS = data.get("args") or {}
    LAST_TOOL_TIME = data.get("timestamp")


subscribe_event("tool_called",track_tool_usage)

subscribe_event("request_started",debug_event)
subscribe_event("request_finished",debug_event)
subscribe_event("request_cancelled",debug_event)
subscribe_event("request_failed",debug_event)
subscribe_event("request_timeout",debug_event)
subscribe_event("request_queued",debug_event)
subscribe_event("request_retry",debug_event)
subscribe_event("request_routed",debug_event)

subscribe_event("request_started",track_last_event)
subscribe_event("request_finished",track_last_event)
subscribe_event("request_failed",track_last_event)
subscribe_event("request_timeout",track_last_event)
subscribe_event("tool_called",track_last_event)
subscribe_event("request_cancelled",track_last_event)

subscribe_event("request_started",track_jarvis_state)
subscribe_event("request_finished",track_jarvis_state)
subscribe_event("request_failed",track_jarvis_state)
subscribe_event("request_timeout",track_jarvis_state)
subscribe_event("tool_called",track_jarvis_state)
subscribe_event("request_cancelled",track_jarvis_state)
