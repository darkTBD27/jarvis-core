
from enum import Enum

from inference.queue_system import queue_size
from inference.runtime_object import RUNTIME_ACCESS

from inference.runtime_errors import get_error_history

from config.runtime_config import (
    HEALTH_ERROR_THRESHOLD,
    HEALTH_DEGRADED_ERROR_THRESHOLD,
    HEALTH_TIMEOUT_THRESHOLD,
    HEALTH_QUEUE_BUSY
)

import time

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

    runtime = RUNTIME_ACCESS
    total = runtime.get_metric("requests_total")

    # --- MIN SAMPLE SIZE (ANTI NOISE) ---
    if total < 10:
        return 0.0

    errors = len(get_error_history())

    return errors / total


def _calculate_timeout_rate():

    from inference.runtime_errors import get_error_types

    runtime = RUNTIME_ACCESS
    total = runtime.get_metric("requests_total")

    # --- MIN SAMPLE SIZE (ANTI NOISE) ---
    if total < 10:
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

    history = runtime.read("health_history")

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

    errors = rt.get_metric("requests_error")
    timeouts = rt.get_metric("requests_timeout")
    slow = rt.get_metric("slow_requests")

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
    return None

# ============================================================
# PUBLIC API
# ============================================================

def get_runtime_health():
    return None


def get_error_intelligence():

    categories = get_recent_error_categories()

    return {
        "recent_categories": categories,
        "config_errors": categories.get("CONFIG_ERROR", 0),
        "dependency_errors": categories.get("DEPENDENCY_ERROR", 0),
        "network_errors": categories.get("NETWORK_ERROR", 0),
        "timeout_errors": categories.get("TIMEOUT_ERROR", 0)
    }
