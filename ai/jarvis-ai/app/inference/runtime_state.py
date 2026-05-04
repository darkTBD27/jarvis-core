# VERIFY MARKER: ~E}$qG}8

from inference.runtime_object import RUNTIME_ACCESS

from engine.logger import logger

from inference.runtime_errors import get_last_error
from inference.runtime_errors import get_error_types
from inference.runtime_errors import get_error_history

from enum import Enum

import time

MAX_EVENT_HISTORY = 100


class RuntimePhase(str, Enum):
    QUEUE = "queue"
    WORKER = "worker"
    RUNTIME_BUSY = "runtime_busy"
    EXECUTION = "execution"
    METRICS = "metrics"
    HISTORY = "history"
    EVENTS = "events"
    SIGNALS = "signals"
    DECISION = "decision"
    ACTION = "action"
    RUNTIME_IDLE = "runtime_idle"


class InvalidRuntimePhase(Exception):
    pass


def validate_phase(phase: str) -> RuntimePhase:
    try:
        return RuntimePhase(phase)
    except ValueError:
        raise InvalidRuntimePhase(f"Invalid runtime phase: {phase}")


def add_runtime_event(event_type, data=None):

    entry = {
        "type": event_type,
        "time": time.time(),
        "data": data or {}
    }

    data_list = RUNTIME_ACCESS.read("runtime_events")

    if len(data_list) >= MAX_EVENT_HISTORY:
        data_list.pop(0)

    data_list.append(entry)

    RUNTIME_ACCESS.write("runtime_events", data_list)


def get_runtime_events():
    return RUNTIME_ACCESS.read("runtime_events")

def get_runtime_context():
    raise RuntimeError("[RUNTIME VIOLATION] Shadow Context removed. Use RuntimeAccess.")


    logger.info(f"[CTX READ FINAL] keys={list(__RUNTIME_CONTEXT.keys())}")

    return dict(__RUNTIME_CONTEXT)


MODEL_WARM = False
# RUNTIME_ACCESS.write("model_warm", MODEL_WARM)


def get_current_health():
    return RUNTIME_ACCESS.read("health")


def get_last_health():
    return RUNTIME_ACCESS.read("last_health")


def get_last_health_change():
    return RUNTIME_ACCESS.read("last_health_change")


def update_health(new_health):
    raise RuntimeError("[RUNTIME VIOLATION] State mutation only allowed inside Runtime Core.")


def is_busy():
    logger.warning("[STATE READ][DIRECT RUNTIME ACCESS] busy")
    return RUNTIME_ACCESS.read("busy")


def get_busy_state():
    logger.warning("[STATE READ][DIRECT RUNTIME ACCESS] busy")
    return RUNTIME_ACCESS.read("busy")


def get_current_request():
    return RUNTIME_ACCESS.read("current_request")


def get_last_state_change():
    return RUNTIME_ACCESS.read("last_state_change")


def get_request_count():
    data = RUNTIME_ACCESS.read("request_status")
    return len(data)


def get_queue_health():
    return {
        "busy": RUNTIME_ACCESS.read("busy"),
        "current": RUNTIME_ACCESS.read("current_request")
    }


def get_request_status(request_id):
    data = RUNTIME_ACCESS.read("request_status")
    return data.get(request_id)


def get_all_request_status():
    return RUNTIME_ACCESS.read("request_status")
    


def is_request_cancelled(request_id):
    data = RUNTIME_ACCESS.read("cancelled_requests")
    return request_id in data


def get_cancelled_requests():
    return RUNTIME_ACCESS.read("cancelled_requests")


def get_request_history():
    return RUNTIME_ACCESS.read("history")


def get_request_timestamps():
    return RUNTIME_ACCESS.read("request_timestamps")


def get_last_requests(limit=50):

    if limit <= 0:
        return []

    data = RUNTIME_ACCESS.read("history")
    return data[-limit:]


def is_model_warm():
    return RUNTIME_ACCESS.read("model_warm")


def get_start_time():
    return RUNTIME_ACCESS.read("start_time")


def get_uptime():
    return int(time.time() - RUNTIME_ACCESS.read("start_time"))


def get_event_listeners():
    return RUNTIME_ACCESS.read("event_listeners")


def has_event_listeners():
    data = RUNTIME_ACCESS.read("event_listeners")
    return len(data) > 0


def get_listener(event):
    data = RUNTIME_ACCESS.read("event_listeners")
    return data.get(event)


def get_runtime_snapshot():

    start_time = RUNTIME_ACCESS.read("start_time")

    request_status = RUNTIME_ACCESS.read("request_status") or {}

    error_types = get_error_types() or {}

    state = RUNTIME_ACCESS.read("state")

    busy = RUNTIME_ACCESS.read("busy")

    current_request = RUNTIME_ACCESS.read("current_request")

    worker_status = RUNTIME_ACCESS.read("worker_status")

    queue_limit = RUNTIME_ACCESS.read("queue_limit")

    total = len(request_status)

    success = 0
    errors = 0
    timeouts = 0

    for r in request_status.values():
        status = r.get("status")

        if status == "success":
            success += 1
        elif status == "error":
            errors += 1
        elif status == "timeout":
            timeouts += 1

    history = RUNTIME_ACCESS.read("history") or []

    avg_duration = 0
    avg_tokens_per_sec = 0

    if history:
        total_duration = sum(r.get("duration", 0) for r in history)
        total_tps = sum(r.get("tokens_per_sec", 0) for r in history)

        avg_duration = total_duration / len(history)
        avg_tokens_per_sec = total_tps / len(history)

    return {
        "version": "v1",

        "runtime": {
            "state": state,
            "uptime": int(time.time() - start_time),
            "busy": busy,
            "worker": {
                "status": worker_status,
                "target": RUNTIME_ACCESS.read("worker_target_count"),
                "threads": len(RUNTIME_ACCESS.read("worker_threads") or [])
            },

            "queue": {
                "current": current_request,
                "limit": queue_limit
            }
        },

        "metrics": {
            "requests": {
                "total": total,
                "success": success,
                "errors": errors,
                "timeouts": timeouts
            },

            "performance": {
                "avg_duration": avg_duration,
                "tokens_per_sec": avg_tokens_per_sec
            }
        },

        "signals": RUNTIME_ACCESS.read("signal_history")[-10:],

        "decisions": {
            "current": RUNTIME_ACCESS.read("last_decision"),
            "history": RUNTIME_ACCESS.read("decision_history")[-10:]
        },

        "errors": {
            "last": get_last_error(),
            "last_at": RUNTIME_ACCESS.read("last_error_at"),
            "types": error_types,
            "history": get_error_history()[-10:],
            "total": sum(error_types.values()) if error_types else 0
        },

        "history": {
            "requests": [
                {
                    "request_id": r.get("request_id"),
                    "duration": r.get("duration")
                }
                for r in history[-10:]
            ]
        },

        "learning": {
            "action_stats": get_action_stats()
        }
    }


def set_busy(value):
    raise RuntimeError("[RUNTIME VIOLATION] State mutation only allowed inside Runtime Core.")


def set_current_request(request_id):
    raise RuntimeError("[RUNTIME VIOLATION] State mutation only allowed inside Runtime Core.")


def clear_current_request():
    raise RuntimeError("[RUNTIME VIOLATION] State mutation only allowed inside Runtime Core.")


def set_model_warm(value):
    raise RuntimeError("[RUNTIME VIOLATION] State mutation only allowed inside Runtime Core.")


def get_model_warm():
    return RUNTIME_ACCESS.read("model_warm")


def set_request_status(request_id, status):
    raise RuntimeError("[RUNTIME VIOLATION] State mutation only allowed inside Runtime Core.")


def set_runtime_context(phase, key, value):
    raise RuntimeError("[RUNTIME VIOLATION] Shadow Context removed. State must go through RuntimeAccess.")

    validated_phase = validate_phase(phase)

    # Phase darf nicht leer sein
    if phase.strip() == "":
        logger.error(f"[CONTEXT BLOCKED] empty phase")
        return

    # Phase validieren (Phase 3)
    try:
        phase_str = validated_phase.value
    except InvalidRuntimePhase as e:
        logger.error(f"[CONTEXT BLOCKED] {str(e)}")
        return

    phase = validated_phase

    # Allowlist prüfen (Phase 4)

    if phase_str not in ALLOWED_CONTEXT_WRITES:
        logger.error(f"[CONTEXT BLOCKED] no allowlist for phase={phase_str}")
        return


    allowed_keys = ALLOWED_CONTEXT_WRITES[phase_str]

    if key not in allowed_keys:
        logger.error(f"[CONTEXT BLOCKED] invalid key={key} for phase={phase_str}")
        return

    __RUNTIME_CONTEXT[key] = value

    logger.warning(
        f"[CTX WRITE][SHADOW] phase={validated_phase} key={key} file={frame.f_code.co_filename} line={frame.f_lineno}"
    )


def add_request_history(
    request_id,
    status,
    duration,
    tokens=0,
    tokens_per_sec=0,
    error=None,
    prompt=None
):
    raise RuntimeError("[RUNTIME VIOLATION] State mutation only allowed inside Runtime Core.")


def get_worker_heartbeat_age():
    return time.time() - RUNTIME_ACCESS.read("worker_heartbeat")


def get_worker_last_activity_age():
    return time.time() - RUNTIME_ACCESS.read("worker_last_activity")


def get_worker_status():
    return RUNTIME_ACCESS.read("worker_status")


def get_request_event_flow(request_id):
    if not request_id:
        return []

    events = RUNTIME_ACCESS.read("runtime_events") or []

    result = []

    for event in events:
        data = event.get("data") or {}

        if data.get("request_id") == request_id:
            result.append({
                "type": event.get("type"),
                "time": event.get("time"),
                "data": data
            })

    return result
