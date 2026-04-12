# ============================================================
# DECISION BUILDER
# ------------------------------------------------------------
# Zweck:
# Baut eine Decision basierend auf:
# - aktuellen Runtime Signals
# - Runtime Snapshot
#
# Liefert:
# - Decision Object (ohne Action!)
# ============================================================

from decision_engine.signal_service import get_latest_signals
from decision_engine.decision_object import create_decision

from inference.runtime_state import get_runtime_snapshot
from inference.runtime_object import get_runtime

from learning_store import get_action_score

import logging

logger = logging.getLogger("jarvis")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _predict_action(signal_type):

    if signal_type == "QUEUE_PRESSURE":
        return "scale_queue"

    if signal_type == "RUNTIME_IDLE":
        return "scale_down"

    if signal_type == "WORKER_STALLED":
        return "restart_worker"

    return None


# ============================================================
# MAIN ENTRY
# ============================================================

def build_decision():

    # ========================================================
    # RUNTIME SNAPSHOT
    # ========================================================

    runtime_state = get_runtime_snapshot()

    # Normalisieren (immer dict)
    if hasattr(runtime_state, "__dict__"):
        runtime_state = vars(runtime_state)
    elif not isinstance(runtime_state, dict):
        runtime_state = {}

    queue_size = runtime_state.get("queue_size", 0)
    worker_status = runtime_state.get("worker_status", "unknown")
    uptime = runtime_state.get("uptime", 0)
    health = runtime_state.get("health", "unknown")

    # ========================================================
    # SIGNAL INPUT
    # ========================================================

    signals = get_latest_signals()

    if not signals:
        return None

    latest_entry = signals[-1]
    raw_signals = latest_entry.get("signals", [])

    if not raw_signals:
        return None

    # nur gültige dict-signals
    valid_signals = [s for s in raw_signals if isinstance(s, dict)]

    if not valid_signals:
        return None

    trigger_signal = valid_signals[-1]
    signal_types = [s.get("type") for s in valid_signals]

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {
        "recent_signal_entries": signals
    }

    # ========================================================
    # DECISION LOGIC
    # ========================================================

    reasoning = "Initial decision based on runtime signal"
    confidence = 0.5
    priority = 1

    # --- PRIORITY BASED DECISION TREE ---

    if "RUNTIME_INSTABILITY" in signal_types:

        reasoning = "Critical instability detected"

        confidence = 0.9
        priority = 9

        if health == "degraded":
            confidence += 0.05
            priority += 1

    elif "RUNTIME_RISK_HIGH" in signal_types:
        reasoning = "High runtime risk"
        confidence = 0.85
        priority = 8

    elif "WORKER_STALLED" in signal_types:
        reasoning = "Worker stalled"
        confidence = 0.9
        priority = 9

    elif "QUEUE_PRESSURE" in signal_types:

        reasoning = f"Queue pressure detected (size={queue_size})"

        # Basis
        confidence = 0.6
        priority = 5

        # Dynamik
        if queue_size > 5:
            confidence += 0.1
            priority += 1

        if queue_size > 10:
            confidence += 0.1
            priority += 2

        if worker_status == "stalled":
            confidence += 0.1
            priority += 2

    elif "RUNTIME_IDLE" in signal_types:

        reasoning = f"System idle (uptime={uptime}s)"

        confidence = 0.5
        priority = 2

        if uptime > 60:
            confidence += 0.1
            priority += 1

        if queue_size == 0:
            confidence += 0.1


    # ========================================================
    # LEARNING BIAS (SAFE + CONTROLLED)
    # ========================================================

    runtime = get_runtime()

    predicted_action = _predict_action(trigger_signal.get("type"))

    if predicted_action:

        try:
            score = get_action_score(predicted_action, context, runtime)

            # --- sanfter Einfluss ---
            confidence += score * 0.05
            priority += int(score * 1)

            # --- HARD LIMITS ---
            confidence = max(0.0, min(1.0, confidence))
            priority = max(0, min(5, priority))

            reasoning += f" | learning_score={round(score, 2)}"

        except Exception as e:
            logger.warning(f"[LEARNING_ERROR] {e}")


    # ========================================================
    # FINAL NORMALIZATION (GLOBAL)
    # ========================================================

    confidence = max(0.0, min(1.0, confidence))
    priority = max(0, priority)


    # ========================================================
    # DECISION OBJECT
    # ========================================================

    return create_decision(
        trigger_signal=trigger_signal,
        context=context,
        runtime_state=runtime_state,
        reasoning=reasoning,
        confidence=confidence,
        priority=priority,
        action=None
    )


# ============================================================
# DEBUG / TEST ENTRY
# ============================================================

def run_test():

    logger.info("TEST START")

    signals = get_latest_signals()
    logger.info("RAW SIGNALS:", signals)

    decision = build_decision()
    logger.info("DECISION:", decision)

    from inference.runtime_object import get_runtime

    rt = get_runtime()
    logger.info("RUNTIME ID:", id(rt))
    logger.info("SIGNAL HISTORY DIRECT:", rt.signal_history)


if __name__ == "__main__":
    run_test()
