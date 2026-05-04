# ============================================================
# RUNTIME INTELLIGENCE
# ------------------------------------------------------------
# Zweck:
# Analysiert Runtime Zustand und erzeugt PURE Signals
#
# INPUT:
# Runtime State + Metrics + Errors
#
# OUTPUT:
# Signals (roh, ohne Interpretation)
# ============================================================

from inference.runtime_errors import get_recent_error_count
from inference.runtime_object import RUNTIME_ACCESS

import time
import logging

logger = logging.getLogger("jarvis")

# ============================================================
# HELPER
# ============================================================

def clamp(x, min_v=0.0, max_v=1.0):
    return max(min_v, min(max_v, x))

def normalize(value, min_v, max_v):
    if max_v == min_v:
        return 0.0
    return clamp((value - min_v) / (max_v - min_v))

def trend(current, previous, eps=1e-6):
    diff = current - previous
    if abs(diff) < eps:
        return 0
    return 1 if diff > 0 else -1

# ============================================================
# SIGNAL DETECTORS (PURE)
# ============================================================

def detect_queue_pressure(queue, queue_prev):

    level = normalize(queue, 0, 50)
    trend_dir = trend(queue, queue_prev)

    return {
        "type": "QUEUE_PRESSURE",
        "value": queue,
        "trend": trend_dir,
        "level": level,
        "timestamp": time.time()
    }


def detect_request_rate(rate, rate_prev):

    level = normalize(rate, 0, 20)
    trend_dir = trend(rate, rate_prev)

    return {
        "type": "REQUEST_RATE",
        "value": rate,
        "trend": trend_dir,
        "level": level,
        "timestamp": time.time()
    }


def detect_latency(latency, latency_prev):

    level = normalize(latency, 0, 10)
    trend_dir = trend(latency, latency_prev)

    return {
        "type": "LATENCY",
        "value": latency,
        "trend": trend_dir,
        "level": level,
        "timestamp": time.time()
    }


def detect_error_rate(error_rate, error_prev):

    level = normalize(error_rate, 0.0, 0.5)
    trend_dir = trend(error_rate, error_prev)

    return {
        "type": "ERROR_RATE",
        "value": error_rate,
        "trend": trend_dir,
        "level": level,
        "timestamp": time.time()
    }


# ============================================================
# SIGNAL GENERATION (STATELESS + PURE)
# ============================================================

def generate_runtime_signals(runtime):

    from inference.queue_system import queue_size as get_queue_size

    signals = []

    # --- CURRENT VALUES ---
    queue = get_queue_size()
    latency = runtime.metric_get("avg_duration")
    requests_total = runtime.metric_get("requests_total")
    errors = get_recent_error_count(60)

    # --- ERROR RATE ---
    if requests_total > 0:
        error_rate = errors / requests_total
    else:
        error_rate = 0.0

    # --- PREVIOUS VALUES ---
    prev = getattr(runtime, "_prev_metrics", {})

    queue_prev = prev.get("queue", queue)
    latency_prev = prev.get("latency", latency)
    rate_prev = prev.get("rate", 0)
    error_prev = prev.get("error_rate", error_rate)

    # --- REQUEST RATE ---
    last_total = prev.get("requests_total", requests_total)
    delta = requests_total - last_total
    rate = max(delta, 0)

    # ========================================================
    # SIGNALS (ONLY PURE)
    # ========================================================

    signals.append(detect_queue_pressure(queue, queue_prev))
    signals.append(detect_request_rate(rate, rate_prev))
    signals.append(detect_latency(latency, latency_prev))
    signals.append(detect_error_rate(error_rate, error_prev))

    # ========================================================
    # SAVE PREVIOUS STATE (IN RUNTIME → allowed)
    # ========================================================

    runtime._prev_metrics = {
        "queue": queue,
        "latency": latency,
        "rate": rate,
        "error_rate": error_rate,
        "requests_total": requests_total
    }

    return signals


# ============================================================
# MAIN ENTRY
# ============================================================

def get_runtime_intelligence():

    runtime = get_runtime()

    signals = generate_runtime_signals(runtime)

    # --- OBSERVABILITY ---
    logger.info(f"[SIGNALS RAW] {signals}")

    runtime.add_signal_history({
        "signals": signals,
        "time": time.time()
    })

    return {
        "signals": signals
    }
