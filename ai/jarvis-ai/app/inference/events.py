import time
from inference.runtime_object import RUNTIME_ACCESS

# --- BACKBONE STATE ---
EVENT_LISTENERS = {}
LAST_EVENT = None
LAST_EVENT_TIME = 0
JARVIS_STATE = "idle"
LAST_TOOL_USED = None
LAST_TOOL_TIME = 0
LAST_TOOL_ARGS = {}

def subscribe_event(event_name, callback):
    if event_name not in EVENT_LISTENERS:
        EVENT_LISTENERS[event_name] = []
    EVENT_LISTENERS[event_name].append(callback)

def emit_event(event_name, data=None):
    listeners = EVENT_LISTENERS.get(event_name, [])
    for callback in listeners.copy():
        try:
            callback(data, event_name)
        except Exception:
            pass

def debug_event(data, event_type):
    if not data: return
    rid = data.get("request_id", "unknown")
    print(f"[EVENT] {event_type} request={rid}")

def track_last_event(data, event_type):
    global LAST_EVENT, LAST_EVENT_TIME
    LAST_EVENT = event_type
    LAST_EVENT_TIME = time.time()

def track_jarvis_state(data, event):
    global JARVIS_STATE
    states = {
        "request_started": "thinking", "request_queued": "queued",
        "request_finished": "idle", "request_failed": "error",
        "request_timeout": "timeout", "tool_called": "tool",
        "request_cancelled": "idle"
    }
    if event in states:
        JARVIS_STATE = states[event]

def track_tool_usage(data, event):
    global LAST_TOOL_USED, LAST_TOOL_TIME, LAST_TOOL_ARGS
    LAST_TOOL_USED = data.get("tool")
    LAST_TOOL_ARGS = data.get("args") or {}
    LAST_TOOL_TIME = data.get("timestamp")

# --- REGISTRATION ---
# Diese Aufrufe brauchen EVENT_LISTENERS (oben definiert)
subscribe_event("tool_called", track_tool_usage)
subscribe_event("request_started", debug_event)
subscribe_event("request_finished", debug_event)
subscribe_event("request_cancelled", debug_event)
subscribe_event("request_failed", debug_event)
subscribe_event("request_timeout", debug_event)
subscribe_event("request_queued", debug_event)
subscribe_event("request_started", track_last_event)
subscribe_event("request_finished", track_last_event)
subscribe_event("request_failed", track_last_event)
subscribe_event("request_timeout", track_last_event)
subscribe_event("tool_called", track_last_event)
subscribe_event("request_started", track_jarvis_state)
subscribe_event("request_finished", track_jarvis_state)
