from enum import Enum

from inference import metrics
from inference.queue_system import get_queue
from inference.runtime_object import get_runtime
from inference.runtime_errors import get_error_history

from config.runtime_config import (
    HEALTH_ERROR_THRESHOLD,
    HEALTH_DEGRADED_ERROR_THRESHOLD,
    HEALTH_TIMEOUT_THRESHOLD,
    HEALTH_QUEUE_BUSY
)


import time


class HealthState(Enum):

    HEALTHY = "healthy"

    BUSY = "busy"

    DEGRADED = "degraded"

    ERROR = "error"


def _calculate_error_rate():

    if metrics.REQUEST_COUNT == 0:
        return 0.0

    return metrics.ERROR_COUNT / metrics.REQUEST_COUNT


def _calculate_timeout_rate():

    if metrics.REQUEST_COUNT == 0:
        return 0.0

    return metrics.TIMEOUT_COUNT / metrics.REQUEST_COUNT


def has_recent_critical_error(seconds=120):

    now = time.time()

    for e in get_error_history():

        if e.get("severity") == "critical":

            if now - e["time"] <= seconds:

                return True

    return False


def _queue_pressure():

    try:

        size = get_queue().qsize()

        if size == 0:
            return 0

        return size

    except Exception:

        return 0


def calculate_health():

    runtime = get_runtime()

    intel_health = evaluate_runtime_health(runtime)

    error_rate = _calculate_error_rate()

    timeout_rate = _calculate_timeout_rate()

    queue_size = runtime.queue_size

    busy = runtime.busy

    critical_recent = has_recent_critical_error()

    from inference.runtime_errors import is_error_spiking

    spike = is_error_spiking()

    flapping = health_is_flapping(runtime)


    if critical_recent:

        health = HealthState.DEGRADED

    elif error_rate > HEALTH_ERROR_THRESHOLD:

        health = HealthState.ERROR

    elif timeout_rate > HEALTH_TIMEOUT_THRESHOLD:

        health = HealthState.DEGRADED

    elif error_rate > HEALTH_DEGRADED_ERROR_THRESHOLD:

        health = HealthState.DEGRADED

    elif spike:

        health = HealthState.DEGRADED

    elif flapping:

        health = HealthState.DEGRADED

    elif queue_size > HEALTH_QUEUE_BUSY:

        health = HealthState.BUSY

    elif busy:

        health = HealthState.BUSY

    elif intel_health == "degraded":

        health = HealthState.DEGRADED

    else:

        health = HealthState.HEALTHY


    if runtime.get_health() != health.value:

        runtime.set_health(health.value)

        runtime.add_health_history(health.value)


    return health


def evaluate_runtime_health(rt):

    errors = rt.metric_get("requests_error")

    timeouts = rt.metric_get("requests_timeout")

    slow = rt.metric_get("slow_requests")

    if timeouts > 3:

        return "degraded"

    if errors > 5:

        return "degraded"

    if slow > 10:

        return "degraded"

    return "healthy"


def get_runtime_health():

    return calculate_health().value


def health_is_flapping(runtime, window=10):

    history = runtime.get_health_history()

    if len(history) < window:

        return False

    recent = history[-window:]

    changes = 0

    last = recent[0]["state"]

    for h in recent[1:]:

        if h["state"] != last:

            changes += 1

            last = h["state"]

    return changes >= 4
