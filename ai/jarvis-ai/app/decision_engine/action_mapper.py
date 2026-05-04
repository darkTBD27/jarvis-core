# VERIFY MAKER: Xp}@&(AW

import time
import logging

from engine.logger import logger

# ============================================================
# CONFIG
# ============================================================

ACTION_COOLDOWNS = {
    "scale_queue": 10,
    "scale_down": 10,
    "restart_worker": 20
}

# globale Cooldown Speicherung (Action-basiert, erlaubt)
last_action_time = {}

# Mindestanforderungen
MIN_CONFIDENCE = 0.6
MIN_PRIORITY = 3


# ============================================================
# MAIN
# ============================================================

def map_decision_to_action(decision):

    if decision.decision_type != "normal":
        logger.info(f"[ACTION NONE] decision_type={decision.decision_type}")
        return None

    confidence = getattr(decision, "confidence", 0.0)

    meta = getattr(decision, "meta", {}) or {}

    base_conf = meta.get("base_confidence", confidence)
    base_priority = meta.get("base_priority", getattr(decision, "priority", 0))

    priority = getattr(decision, "priority", 0)

    signal = decision.trigger_signal or {}
    signal_type = signal.get("type")

    # ========================================================
    # THRESHOLD CHECK
    # ========================================================

    if base_conf < MIN_CONFIDENCE:
        logger.info(
            f"[ACTION BLOCKED] base confidence too low "
            f"({round(base_conf,3)})"
        )
        return None

    # ========================================================
    # ACTION SELECTION (deterministisch)
    # ========================================================

    action = None

    # --- SCALE UP ---
    if signal_type == "QUEUE_PRESSURE":
        action = "scale_queue"

    # --- SCALE DOWN ---
    elif signal_type == "LATENCY":
        if base_priority >= 5:
            action = "scale_queue"

    # --- RESTART ---
    elif signal_type == "ERROR_RATE":
        if base_conf > 0.8:
            action = "restart_worker"

    if not action:
        logger.info(f"[ACTION NONE] no mapping for signal={signal_type}")
        return None

    # ========================================================
    # COOLDOWN CHECK
    # ========================================================

    now = time.time()
    last_time = last_action_time.get(action, 0)
    cooldown = ACTION_COOLDOWNS.get(action, 5)

    if now - last_time < cooldown:
        logger.info(f"[ACTION BLOCKED] cooldown active ({action})")
        return None

    last_action_time[action] = now

    # ========================================================
    # FINAL
    # ========================================================

    logger.info(
        f"[ACTION] {action} | "
        f"conf={round(base_conf,3)} "
        f"prio={priority} "
        f"base_prio={base_priority} "
        f"signal={signal_type}"
    )

    return action
