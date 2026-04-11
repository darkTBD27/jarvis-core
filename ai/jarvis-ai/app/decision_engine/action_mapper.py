import time
import logging

logger = logging.getLogger("jarvis")

last_action_time = {}

signal_counter = {}
signal_last_seen = {}

SIGNAL_THRESHOLD = 2
SIGNAL_DECAY_TIME = 10  # Sekunden

ACTION_COOLDOWNS = {
    "scale_queue": 10,
    "scale_down": 10,
    "restart_worker": 20
}


def map_decision_to_action(decision):

    signal = decision.trigger_signal

    signal_type = signal.get("type")
    is_stable = signal.get("stable", False)

    confidence = decision.confidence
    priority = decision.priority

    # -------------------------
    # SIGNAL STABILITY CHECK
    # -------------------------
    now = time.time()

    # --- DECAY CHECK ---
    last_seen = signal_last_seen.get(signal_type)

    if last_seen and (now - last_seen > SIGNAL_DECAY_TIME):
        signal_counter[signal_type] = 0

    # --- COUNT ---
    count = signal_counter.get(signal_type, 0) + 1
    signal_counter[signal_type] = count
    signal_last_seen[signal_type] = now

    logger.info(f"[DEBUG] signal={signal_type} count={count}")

    if count < SIGNAL_THRESHOLD:
        return None

    # -------------------------
    # QUALITY FILTER
    # -------------------------
    if confidence < 0.6:
        return None

    if priority < 3:
        return None

    # -------------------------
    # SIGNAL → ACTION
    # -------------------------
    if signal_type == "QUEUE_PRESSURE" and is_stable:
        action = "scale_queue"

    elif signal_type == "RUNTIME_IDLE" and is_stable:
        if decision.runtime_state_snapshot.get("uptime", 0) > 30:
            action = "scale_down"
        else:
            return None

    elif signal_type == "WORKER_STALLED":
        action = "restart_worker"

    else:
        return None

    # -------------------------
    # COOLDOWN
    # -------------------------
    now = time.time()
    last_time = last_action_time.get(action, 0)
    cooldown = ACTION_COOLDOWNS.get(action, 5)

    if now - last_time < cooldown:
        return None

    last_action_time[action] = now

    return action
