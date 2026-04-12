# ============================================================
# RUNTIME INTELLIGENCE
# ------------------------------------------------------------
# Zweck:
# Analysiert Runtime Zustand und erzeugt Signals
#
# INPUT:
# Runtime State + Errors + Queue
#
# OUTPUT:
# Signals (keine Decisions, keine Actions!)
# ============================================================

from inference.runtime_errors import get_recent_error_count
from inference.runtime_object import get_runtime

import time
import logging

logger = logging.getLogger("jarvis")

# ============================================================
# CONFIG
# ============================================================

signal_memory = {}

SIGNAL_STABILITY_THRESHOLD = 2
SIGNAL_WINDOW = 10  # Sekunden

# ============================================================
# ANALYSIS LAYER
# ============================================================

def analyze_error_patterns():
    return {
        "last_minute": get_recent_error_count(60),
        "last_5_minutes": get_recent_error_count(300)
    }


def calculate_stability_score():
    errors = get_recent_error_count(60)

    if errors == 0:
        return 100
    if errors < 3:
        return 85
    if errors < 6:
        return 70
    if errors < 10:
        return 50

    return 25


def detect_runtime_risk():
    errors = get_recent_error_count(60)

    if errors > 8:
        return "high"
    if errors > 3:
        return "medium"

    return "low"


def detect_error_trend():
    last_min = get_recent_error_count(60)
    last_5min = get_recent_error_count(300)

    if last_min > last_5min / 5:
        return "increasing"

    if last_min < last_5min / 10:
        return "decreasing"

    return "stable"


def detect_instability(trend):
    errors = get_recent_error_count(60)

    if errors > 8:
        return "critical"

    if trend == "increasing" and errors > 3:
        return "warning"

    return "stable"

# ============================================================
# SIGNAL CORE
# ============================================================

def create_signal(signal_type):

    now = time.time()

    entries = signal_memory.get(signal_type, [])
    entries = [t for t in entries if now - t < SIGNAL_WINDOW]

    entries.append(now)
    signal_memory[signal_type] = entries

    stable = len(entries) >= SIGNAL_STABILITY_THRESHOLD

    signal = {
        "type": signal_type,
        "timestamp": now,
        "source": "runtime_intelligence",
        "stable": stable
    }

    logger.info(f"[SIGNAL] {signal_type} stable={stable}")

    return signal


# ============================================================
# SIGNAL DETECTORS
# ============================================================

def detect_queue_pressure(queue_size):
    if queue_size > 2:
        return create_signal("QUEUE_PRESSURE")
    return None


# ============================================================
# SIGNAL GENERATION
# ============================================================

def generate_runtime_signals(runtime, intelligence):

    signals = []

    queue = runtime.queue_size
    worker = runtime.get_worker_status()

    # --- QUEUE ---
    queue_signal = detect_queue_pressure(queue)
    if queue_signal:
        signals.append(queue_signal)

    # --- WORKER ---
    if worker == "stalled":
        signals.append(create_signal("WORKER_STALLED"))

    # --- LOAD ---
    if runtime.is_busy() and queue > 3:
        signals.append(create_signal("RUNTIME_OVERLOAD"))

    # --- IDLE ---
    if not runtime.is_busy() and queue == 0:
        signals.append(create_signal("RUNTIME_IDLE"))

    # --- RISK ---
    if intelligence["risk_level"] == "high":
        signals.append(create_signal("RUNTIME_RISK_HIGH"))

    # --- INSTABILITY ---
    if intelligence["instability"] == "critical":
        signals.append(create_signal("RUNTIME_INSTABILITY"))

    # --- TREND ---
    if intelligence["error_trend"] == "increasing":
        signals.append(create_signal("ERROR_TREND_UP"))

    elif intelligence["error_trend"] == "decreasing":
        signals.append(create_signal("ERROR_RECOVERY"))

    # --- STABILITY DROP ---
    if intelligence["stability_score"] < 60:
        signals.append(create_signal("STABILITY_DROP"))

    # --- FALLBACK ---
    if not signals:
        signals.append(create_signal("RUNTIME_IDLE"))

    return signals


# ============================================================
# MAIN ENTRY
# ============================================================

def get_runtime_intelligence():

    runtime = get_runtime()

    trend = detect_error_trend()

    intelligence = {
        "error_patterns": analyze_error_patterns(),
        "stability_score": calculate_stability_score(),
        "risk_level": detect_runtime_risk(),
        "error_trend": trend,
        "instability": detect_instability(trend)
    }

    signals = generate_runtime_signals(runtime, intelligence)

    runtime.add_signal_history(signals)

    intelligence["signals"] = signals

    logger.info(f"[INTELLIGENCE] signals={len(signals)}")

    return intelligence
