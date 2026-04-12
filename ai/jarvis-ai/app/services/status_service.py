# ============================================================
# STATUS SERVICE
# ------------------------------------------------------------
# Zweck:
# Liefert aktuellen Runtime-Zustand für Dashboard
#
# Enthält:
# - Runtime State
# - Worker Status
# - Performance
# - Errors
# - Signals
# - Learning (Action Verhalten)
# ============================================================

from inference.runtime_health import get_runtime_health
from inference.runtime_health import get_error_intelligence

from inference.runtime_object import get_runtime

from inference.runtime_intelligence import get_runtime_intelligence

from learning_store import get_learning_state


# ============================================================
# MAIN ENTRY
# ============================================================

def get_status():

    rt = get_runtime()

    intelligence = get_runtime_intelligence()
    learning = get_learning_state()

    # ========================================================
    # CORE STATE
    # ========================================================

    core = {
        "state": rt.state,
        "uptime": rt.get_uptime(),
        "busy": rt.busy,
        "health": get_runtime_health()
    }

    # ========================================================
    # WORKER
    # ========================================================

    worker = {
        "status": rt.get_worker_status(),
        "heartbeat_age": rt.get_worker_heartbeat_age(),
        "last_activity": rt.get_worker_last_activity_age()
    }

    # ========================================================
    # QUEUE
    # ========================================================

    queue = {
        "size": rt.queue_size,
        "limit": 0
    }

    # ========================================================
    # PERFORMANCE
    # ========================================================

    performance = {
        "tokens_per_sec": rt.metric_get("tokens_per_sec"),
        "last_duration": rt.metric_get("last_duration"),
        "avg_duration": rt.metric_get("avg_duration"),
        "total_requests": rt.metric_get("requests_total"),
        "success_requests": rt.metric_get("requests_success"),
        "slow_requests": rt.metric_get("slow_requests")
    }

    # ========================================================
    # ERRORS
    # ========================================================

    errors = {
        "last_error": rt.get_last_error(),
        "error_types": rt.get_error_types(),
        "error_history": rt.get_error_history(),
        "timeouts": rt.metric_get("requests_timeout")
    }

    # ========================================================
    # ACTIVITY
    # ========================================================

    activity = {
        "current_request": rt.current_request,
        "last_request": rt.last_request,
        "history": rt.history,
        "runtime_events": rt.get_runtime_events()[-10:]
    }

    # ========================================================
    # SIGNALS
    # ========================================================

    signals = {
        "signal_history": rt.signal_history
    }

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {

        "jarvis": {
            "state": core["state"],
            "uptime": core["uptime"]
        },

        "busy": core["busy"],
        "health": core["health"],

        "queue": queue["size"],
        "queue_limit": queue["limit"],

        "worker_status": worker["status"],
        "worker_heartbeat_age": worker["heartbeat_age"],
        "worker_last_activity": worker["last_activity"],

        "current_request": activity["current_request"],
        "last_request": activity["last_request"],

        "history": activity["history"],
        "runtime_events": activity["runtime_events"],

        "tokens_per_sec": performance["tokens_per_sec"],
        "last_duration": performance["last_duration"],
        "avg_duration": performance["avg_duration"],
        "total_requests": performance["total_requests"],
        "success_requests": performance["success_requests"],
        "slow_requests": performance["slow_requests"],

        "last_error": errors["last_error"],
        "error_types": errors["error_types"],
        "error_history": errors["error_history"],
        "timeouts": errors["timeouts"],

        "error_intelligence": intelligence,

        "signal_history": signals["signal_history"],

        # LEARNING
        "learning": learning
    }
