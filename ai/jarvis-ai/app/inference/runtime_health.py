# ============================================================
# RUNTIME HEALTH SYSTEM
# ------------------------------------------------------------
# Zweck:
# Bestimmt den aktuellen Gesundheitszustand der Runtime
#
# Wichtig:
# Health ist ein STABILER Zustand, keine Momentaufnahme!
# ============================================================

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

# ============================================================
# CONFIG
# ============================================================

MIN_HEALTH_DURATION = 5  # Sekunden (Anti-Flapping)

# ============================================================
# HEALTH STATES
# ============================================================

class HealthState(Enum):

    HEALTHY = "healthy"
    BUSY = "busy"
    DEGRADED = "degraded"
    ERROR = "error"

# ============================================================
# METRIC CALCULATION
# ============================================================

def _calculate_error_rate():

    total = metrics.REQUEST_COUNT

    if total == 0:
        return 0.0

    errors = len(get_error_history())

    return errors / total


def _calculate_timeout_rate():

    from inference.runtime_errors import get_error_types

    total = metrics.REQUEST_COUNT

    if total == 0:
        return 0.0

    timeouts = get_error_types().get("TimeoutError", 0)

    return timeouts / total

# ============================================================
# ERROR ANALYSIS
# ============================================================

def has_recent_critical_error(seconds=120):

    now = time.time()

    for e in get_error_history():

        if e.get("severity") == "critical":
            if now - e["time"] <= seconds:
                return True

        if e.get("category") in ("CONFIG_ERROR", "DEPENDENCY_ERROR"):
            return True

    return False


def get_recent_error_categories(seconds=120):

    now = time.time()
    categories = {}

    for e in get_error_history():

        if now - e["time"] <= seconds:

            cat = e.get("category", "UNKNOWN")
            categories[cat] = categories.get(cat, 0) + 1

    return categories

# ============================================================
# HEALTH STABILITY CHECK
# ============================================================

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

# ============================================================
# INTERNAL HEALTH EVALUATION
# ============================================================

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

# ============================================================
# MAIN HEALTH CALCULATION
# ============================================================

def calculate_health():

    runtime = get_runtime()

    # --- INPUT ---
    intel_health = evaluate_runtime_health(runtime)
    error_rate = _calculate_error_rate()
    timeout_rate = _calculate_timeout_rate()

    queue_size = runtime.queue_size
    busy = runtime.busy

    critical_recent = has_recent_critical_error()

    from inference.runtime_errors import is_error_spiking
    spike = is_error_spiking()

    recent_categories = get_recent_error_categories()
    flapping = health_is_flapping(runtime)

    # ========================================================
    # DECISION TREE
    # ========================================================

    if critical_recent:
        health = HealthState.DEGRADED

    elif error_rate > HEALTH_ERROR_THRESHOLD and spike:
        health = HealthState.ERROR

    elif timeout_rate > HEALTH_TIMEOUT_THRESHOLD:
        health = HealthState.DEGRADED

    elif error_rate > HEALTH_DEGRADED_ERROR_THRESHOLD:
        health = HealthState.DEGRADED

    elif recent_categories.get("CONFIG_ERROR", 0) >= 2:
        health = HealthState.ERROR

    elif recent_categories.get("DEPENDENCY_ERROR", 0) >= 2:
        health = HealthState.DEGRADED

    elif spike:
        health = HealthState.DEGRADED

    elif flapping:
        health = HealthState.DEGRADED

    elif queue_size > HEALTH_QUEUE_BUSY and not critical_recent:
        health = HealthState.BUSY

    elif busy and error_rate < HEALTH_DEGRADED_ERROR_THRESHOLD:
        health = HealthState.BUSY

    elif intel_health == "degraded" and not flapping:
        health = HealthState.DEGRADED

    else:
        health = HealthState.HEALTHY

    # ========================================================
    # STABILIZATION (ANTI-FLAPPING)
    # ========================================================

    current = runtime.get_health()
    now = time.time()

    last_change_time = getattr(runtime, "health_last_change", 0)

    if current != health.value:

        if now - last_change_time >= MIN_HEALTH_DURATION:

            runtime.set_health(health.value)
            runtime.add_health_history(health.value)
            runtime.health_last_change = now

    return health

# ============================================================
# PUBLIC API
# ============================================================

def get_runtime_health():
    return calculate_health().value


def get_error_intelligence():

    categories = get_recent_error_categories()

    return {
        "recent_categories": categories,
        "config_errors": categories.get("CONFIG_ERROR", 0),
        "dependency_errors": categories.get("DEPENDENCY_ERROR", 0),
        "network_errors": categories.get("NETWORK_ERROR", 0),
        "timeout_errors": categories.get("TIMEOUT_ERROR", 0)
    }
