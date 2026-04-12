# ============================================================
# ACTION MAPPER
# ------------------------------------------------------------
# Zweck:
# Mappt Decision → Action unter Berücksichtigung von:
# - Signal Stabilität
# - Confidence / Priority
# - Cooldowns
# - Learning Feedback (Phase 5.2)
# ============================================================

from learning_store import get_action_score

import time
import logging

logger = logging.getLogger("jarvis")

# ============================================================
# STATE (Runtime-intern, kein globaler Runtime-State!)
# ============================================================

last_action_time = {}

signal_counter = {}
signal_last_seen = {}

# ============================================================
# CONFIG
# ============================================================

SIGNAL_THRESHOLD = 2
SIGNAL_DECAY_TIME = 10  # Sekunden

ACTION_COOLDOWNS = {
    "scale_queue": 10,
    "scale_down": 10,
    "restart_worker": 20
}

# ============================================================
# MAIN MAPPING FUNCTION
# ============================================================

def map_decision_to_action(decision):

    signal = decision.trigger_signal

    signal_type = signal.get("type")
    is_stable = signal.get("stable", False)

    confidence = decision.confidence
    priority = decision.priority

    # ========================================================
    # SIGNAL STABILITY (COUNT + DECAY)
    # ========================================================

    now = time.time()

    last_seen = signal_last_seen.get(signal_type)

    if last_seen and (now - last_seen > SIGNAL_DECAY_TIME):
        signal_counter[signal_type] = 0

    count = signal_counter.get(signal_type, 0) + 1
    signal_counter[signal_type] = count
    signal_last_seen[signal_type] = now

    logger.info(f"[DEBUG] signal={signal_type} count={count}")

    # ========================================================
    # BALANCED TRIGGER LOGIC
    # ========================================================

    # --- Mindest-Stabilität ---
    if count < 2:
        return None

    # --- Adaptive Confidence ---
    if is_stable:
        min_conf = 0.5
    else:
        min_conf = 0.65

    if confidence < min_conf:
        return None

    # --- Adaptive Priority ---
    if is_stable:
        min_prio = 2
    else:
        min_prio = 4

    if priority < min_prio:
        return None

    # --- ACTION COOLDOWN ---
    last_exec = last_action_time.get(signal_type)

    if last_exec and (time.time() - last_exec < 3):
        return None

    last_action_time[signal_type] = time.time()

    # ========================================================
    # SIGNAL → ACTION MAPPING
    # ========================================================

    action = None

    if signal_type == "QUEUE_PRESSURE" and is_stable:
        action = "scale_queue"

    elif signal_type == "RUNTIME_IDLE" and is_stable:
        if decision.runtime_state_snapshot.get("uptime", 0) > 30:
            action = "scale_down"

    elif signal_type == "WORKER_STALLED":
        action = "restart_worker"

    if not action:
        return None

    logger.info(f"[ACTION_CHECK] signal={signal_type} stable={is_stable} conf={confidence} prio={priority}")
    logger.info(f"[ACTION_RESULT] action={action}")

    # ========================================================
    # COOLDOWN CHECK
    # ========================================================

    now = time.time()
    last_time = last_action_time.get(action, 0)
    cooldown = ACTION_COOLDOWNS.get(action, 5)

    if now - last_time < cooldown:
        return None

    last_action_time[action] = now

    # ========================================================
    # FINAL ACTION
    # ========================================================

    return action
