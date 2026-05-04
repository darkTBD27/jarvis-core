# ============================================================
# DECISION BUILDER
# ------------------------------------------------------------
# Zweck:
# Baut eine Decision basierend auf PURE Signals
#
# INPUT:
# - Signals (QUEUE_PRESSURE, REQUEST_RATE, LATENCY, ERROR_RATE)
#
# OUTPUT:
# - Decision Object (ohne Action!)
# ============================================================

from decision_engine.signal_service import get_latest_signals
from decision_engine.decision_object import create_decision

# TODO PHASE 6:
# runtime_snapshot umgeht RuntimeAccess
# aktuell read-only toleriert
from inference.runtime_state import get_runtime_snapshot

import logging

logger = logging.getLogger("jarvis")


# ============================================================
# HELPER
# ============================================================

def _get_signal(signals, signal_type):
    for s in signals:
        if s.get("type") == signal_type:
            return s
    return None


def _count_active(signals, threshold=0.3):
    return sum(1 for s in signals if s.get("level", 0) >= threshold)


# ============================================================
# MAIN ENTRY
# ============================================================

def build_decision(signals):

    # PHASE 3: tolerierter read-only Parallelzustandszufluss hinter dem Validierungsgate
    # Signals bleiben Primärpfad, Runtime-Snapshot ist sekundärer Kontext und kein Entscheidungs-Eintritt

    runtime_state = get_runtime_snapshot()

    if hasattr(runtime_state, "__dict__"):
        runtime_state = vars(runtime_state)
    elif not isinstance(runtime_state, dict):
        runtime_state = {}

    # ========================================================
    # SIGNAL INPUT
    # ========================================================

    if not signals:
        logger.info("[DECISION NONE] no signals in latest entry")
        return None

    signals = [s for s in signals if isinstance(s, dict)]

    if not signals:
        logger.info("[DECISION NONE] invalid signals format")
        return None

    # ========================================================
    # DEBUG: RAW SIGNALS
    # ========================================================

    logger.info(f"[DECISION INPUT] signals={signals}")

    # ========================================================
    # SIGNAL EXTRACTION
    # ========================================================

    queue = _get_signal(signals, "QUEUE_PRESSURE")
    rate = _get_signal(signals, "REQUEST_RATE")
    latency = _get_signal(signals, "LATENCY")
    error = _get_signal(signals, "ERROR_RATE")

    active_signals = _count_active(signals)

    required_signals = ["QUEUE_PRESSURE", "REQUEST_RATE", "LATENCY", "ERROR_RATE"]

    missing_signals = [
        s for s in required_signals
        if not any(sig.get("type") == s and sig.get("level", 0) >= 0.3 for sig in signals)
    ]

    logger.info(
        f"[DECISION ACTIVE] count={active_signals} "
        f"queue={queue} rate={rate} latency={latency} error={error}"
    )

    if active_signals < 2:

        logger.info(
            f"[DECISION NONE] not enough active signals "
            f"(required=2, actual={active_signals})"
        )

        decision = create_decision(
            trigger_signal=signals[-1],
            context={"signals": signals},
            runtime_state=runtime_state,
            reasoning=f"not enough active signals ({active_signals}/2)",
            confidence=0.0,
            priority=0,
            action=None,
            decision_type="none",
            meta={
                "active": active_signals,
                "required": 2,
                "missing": missing_signals
            }
        )

        return decision

    # ========================================================
    # BASE VALUES
    # ========================================================

    reasoning_parts = []
    confidence = 0.0
    priority = 0

    debug_steps = []

    # ========================================================
    # ERROR
    # ========================================================

    if error:
        lvl = error["level"]
        tr = error["trend"]

        if lvl > 0.2:
            conf_add = 0.4 + lvl * 0.5
            prio_add = 4

            if tr > 0:
                conf_add += 0.1
                prio_add += 2
                reasoning_parts.append("error increasing")
            else:
                reasoning_parts.append("error present")

            confidence += conf_add
            priority += prio_add

            debug_steps.append(f"ERROR +conf={round(conf_add,3)} +prio={prio_add}")

    # ========================================================
    # QUEUE
    # ========================================================

    if queue:
        lvl = queue["level"]
        tr = queue["trend"]

        if lvl > 0.2:
            conf_add = 0.2 + lvl * 0.4
            prio_add = 2

            if tr > 0:
                conf_add += 0.1
                prio_add += 1
                reasoning_parts.append("queue rising")
            else:
                reasoning_parts.append("queue load")

            confidence += conf_add
            priority += prio_add

            debug_steps.append(f"QUEUE +conf={round(conf_add,3)} +prio={prio_add}")

    # ========================================================
    # RATE
    # ========================================================

    if rate:
        lvl = rate["level"]
        tr = rate["trend"]

        if lvl > 0.2:
            conf_add = 0.15 + lvl * 0.3
            prio_add = 2

            if tr > 0:
                conf_add += 0.05
                prio_add += 1
                reasoning_parts.append("request burst")
            else:
                reasoning_parts.append("request activity")

            confidence += conf_add
            priority += prio_add

            debug_steps.append(f"RATE +conf={round(conf_add,3)} +prio={prio_add}")

    # ========================================================
    # LATENCY
    # ========================================================

    if latency:
        lvl = latency["level"]
        tr = latency["trend"]

        if lvl > 0.2:
            conf_add = 0.25 + lvl * 0.4
            prio_add = 3

            if tr > 0:
                conf_add += 0.1
                prio_add += 1
                reasoning_parts.append("latency rising")
            else:
                reasoning_parts.append("latency high")

            confidence += conf_add
            priority += prio_add

            debug_steps.append(f"LATENCY +conf={round(conf_add,3)} +prio={prio_add}")

    # ========================================================
    # COMBINATION BOOST
    # ========================================================

    if active_signals >= 3:
        confidence += 0.1
        priority += 1
        debug_steps.append("BOOST 3 signals")

    if active_signals == 4:
        confidence += 0.1
        priority += 1
        debug_steps.append("BOOST 4 signals")

    # ========================================================
    # NORMALIZATION
    # ========================================================

    confidence = max(0.0, min(1.0, confidence))
    priority = max(0, min(10, priority))
    priority = int(round(priority))

    reasoning = ", ".join(reasoning_parts) if reasoning_parts else "weak signal state"

    weight = confidence * priority

    # ========================================================
    # FINAL DEBUG OUTPUT
    # ========================================================

    logger.info(f"[DECISION STEPS] {debug_steps}")

    logger.info(
        f"[DECISION RESULT] "
        f"conf={round(confidence,3)} "
        f"prio={priority} "
        f"weight={round(weight,3)} "
        f"reason={reasoning}"
    )

    base_confidence = confidence

    base_priority = priority

    # ========================================================
    # CONTROLLED LEARNING (CONFIDENCE ONLY)
    # ========================================================

    from learning.learning_runtime import (
        get_confidence_adjustment,
        get_priority_adjustment
    )
    from learning_store import get_action_score

    signal_type = signals[-1].get("type")

    score = get_action_score(
        signal_type,
        runtime=runtime_state
    ) or 0.0

    # --- SCORE HARD LIMIT ---
    if score > 1.0:
        score = 1.0
    elif score < -1.0:
        score = -1.0

    # --- SCORE → CONFIDENCE MAPPING ---
    learning_adjustment = score * 0.05

    # --- SCORE DEADZONE ---
    if abs(score) < 0.05:
        learning_adjustment = 0.0
    else:
        # --- SCORE → CONFIDENCE MAPPING ---
        learning_adjustment = score * 0.05

    priority_adjustment = 0.0

    logger.info(
        f"[LEARNING SCORE] signal={signal_type} "
        f"score={round(score,5)} "
        f"mapped={round(learning_adjustment,5)}"
    )

    # --- HARD LIMIT ---
    learning_adjustment = max(-0.05, min(0.05, learning_adjustment))

    # --- DEADZONE ---
    if abs(learning_adjustment) >= 0.003:

        old_conf = confidence

        # nur confidence beeinflussen
        confidence += learning_adjustment

        # clamp
        confidence = max(0.0, min(1.0, confidence))

        logger.info(
            f"[LEARNING] signal={signal_type} "
            f"adj={round(learning_adjustment,4)} "
            f"conf={round(old_conf,3)}->{round(confidence,3)}"
        )
    else:
        logger.debug(
            f"[LEARNING SKIP] adjustment too small ({round(learning_adjustment,5)})"
        )

    # ========================================================
    # CONTROLLED LEARNING (PRIORITY)
    # ========================================================

    # --- HARD LIMIT ---
    if priority_adjustment > 1.0:
        priority_adjustment = 1.0
    elif priority_adjustment < -1.0:
        priority_adjustment = -1.0

    # --- DEADZONE ---
    if abs(priority_adjustment) >= 0.1:

        old_prio = priority

        priority += priority_adjustment

        # clamp
        priority = max(0, min(10, priority))

        logger.info(
            f"[LEARNING PRIORITY APPLY] signal={signal_type} "
            f"adj={round(priority_adjustment,3)} "
            f"prio={old_prio}->{priority}"
        )
    else:
        logger.debug(
            f"[LEARNING PRIORITY SKIP] too small ({round(priority_adjustment,3)})"
        )

    # ========================================================
    # DECISION RETURN
    # ========================================================

    decision = create_decision(
        trigger_signal=signals[-1],
        context={"signals": signals},
        runtime_state=runtime_state,
        reasoning=reasoning,
        confidence=confidence,
        priority=priority,
        action=None,
        decision_type="normal",
        meta={
            "active": active_signals,
            "required": 2,
            "missing": missing_signals,

            # --- LEARNING OBSERVABILITY ---
            "base_confidence": round(base_confidence, 5),
            "learning_adjustment": round(learning_adjustment, 5),
            "final_confidence": round(confidence, 5),

            "base_priority": base_priority,
            "learning_adjustment_priority": round(priority_adjustment, 5),
            "final_priority": priority
        }
    )

    return decision
