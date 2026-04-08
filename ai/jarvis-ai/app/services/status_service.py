from inference.runtime_health import get_runtime_health
from inference.runtime_health import get_error_intelligence

from inference.runtime_object import get_runtime

from inference.runtime_state import get_last_error
from inference.runtime_state import get_error_types

from inference.runtime_intelligence import get_runtime_intelligence

def get_status():

    rt = get_runtime()

    engine = {

        "jarvis_state": rt.state,

        "uptime": rt.get_uptime(),

        "busy": rt.busy,

        "queue": rt.queue_size,

        "queue_limit": 0,

        "current_request": rt.current_request,

        "queued_requests": [],

        "last_tool": "none",

        "worker_status": rt.get_worker_status(),

        "worker_heartbeat_age": rt.get_worker_heartbeat_age(),

        "worker_last_activity": rt.get_worker_last_activity_age(),

        "errors": rt.metric_get("requests_error"),

        "timeouts": rt.metric_get("requests_timeout"),

        "success_requests": rt.metric_get("requests_success"),

        "total_requests": rt.metric_get("requests_total"),

        "tokens_per_sec": rt.metric_get("tokens_per_sec"),

        "last_duration": rt.metric_get("last_duration"),

        "avg_duration": rt.metric_get("avg_duration"),

        "last_success_request": rt.metric_get("last_success_request"),

        "last_error": rt.get_last_error(),

        "error_types": rt.get_error_types(),

        "last_event": None,

        "history": rt.history,

        "health": rt.get_health(),

        "error_types": rt.get_error_types(),

        "last_error": rt.get_last_error(),

        "runtime_events": rt.get_runtime_events()[-10:]

    }

    status = {

        "jarvis":{

            "state": engine.get("jarvis_state","unknown"),

            "uptime": engine.get("uptime",0)

        },

        "busy": engine.get("busy",False),

        "queue": engine.get("queue",0),

        "queue_limit": engine.get("queue_limit",0),

        "current_request": engine.get("current_request"),

        "queued_requests": engine.get("queued_requests",[]),

        "last_tool": engine.get("last_tool","none"),

        "errors": engine.get("errors",0),

        "timeouts": engine.get("timeouts",0),

        "success_requests": engine.get("success_requests",0),

        "total_requests": engine.get("total_requests",0),

        "tokens_per_sec": engine.get("tokens_per_sec",0),

        "last_duration": engine.get("last_duration",0),

        "avg_duration": engine.get("avg_duration",0),

        "last_success_request": engine.get("last_success_request"),

        "last_error": engine.get("last_error"),

        "last_event": engine.get("last_event"),

        "history": engine.get("history",[]),

        "health": get_runtime_health(),

        "error_intelligence": get_runtime_intelligence()

    }

    return {

        "jarvis":{
            "state": engine.get("jarvis_state"),
            "uptime": engine.get("uptime")
        },

        "busy": engine.get("busy"),

        "queue": engine.get("queue"),

        "queue_limit": engine.get("queue_limit"),

        "current_request": engine.get("current_request"),

        "queued_requests": engine.get("queued_requests"),

        "last_tool": engine.get("last_tool"),

        "worker_status": engine.get("worker_status"),

        "worker_heartbeat_age": engine.get("worker_heartbeat_age"),

        "worker_last_activity": engine.get("worker_last_activity"),

        "errors": engine.get("errors"),

        "timeouts": engine.get("timeouts"),

        "success_requests": engine.get("success_requests"),

        "total_requests": engine.get("total_requests"),

        "tokens_per_sec": engine.get("tokens_per_sec"),

        "last_duration": engine.get("last_duration"),

        "avg_duration": engine.get("avg_duration"),

        "last_success_request": engine.get("last_success_request"),

        "last_error": engine.get("last_error"),

        "last_event": engine.get("last_event"),

        "history": engine.get("history"),

        "health": engine.get("health"),

        "last_request": rt.last_request,

        "error_types": rt.get_error_types(),

        "error_history": rt.get_error_history(),

        "error_intelligence": get_runtime_intelligence(),

        "runtime_events": rt.get_runtime_events()[-10:]

    }
