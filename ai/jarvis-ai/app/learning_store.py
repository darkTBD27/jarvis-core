# ============================================================
# LEARNING STORE
# ------------------------------------------------------------
# Zweck:
# Speichert Bewertung von Actions basierend auf Outcomes
#
# Struktur:
# action → context_key → stats
# ============================================================

# ============================================================
# STORAGE
# ============================================================

learning = {}


# ============================================================
# CONFIG
# ============================================================

MIN_SAMPLES = 3        # bevor Learning greift
DECAY_FACTOR = 0.9     # alte Werte verlieren Gewicht
MAX_SCORE = 1.0        # clamp


# ============================================================
# CONTEXT BUILDER
# ------------------------------------------------------------
# Wandelt Outcome → Kontext-Key
# ============================================================

def build_context_key(outcome=None, runtime=None):

    if outcome is not None:
        queue = getattr(outcome, "queue_before", 0)
    elif runtime is not None:
        queue = getattr(runtime, "queue_size", 0)
    else:
        return "QUEUE_UNKNOWN"

    if queue == 0:
        return "QUEUE_0"

    if queue < 3:
        return "QUEUE_LOW"

    if queue < 6:
        return "QUEUE_MEDIUM"

    return "QUEUE_HIGH"


# ============================================================
# UPDATE LEARNING
# ------------------------------------------------------------
# Speichert Ergebnis einer Action im Kontext
# ============================================================

def update_learning(action, result, outcome):

    action = str(action).upper()

    key = build_context_key(outcome)

    if action not in learning:
        learning[action] = {}

    if key not in learning[action]:
        learning[action][key] = {
            "GOOD": 0.0,
            "BAD": 0.0,
            "NEUTRAL": 0.0
        }

    # -------------------------------------------------
    # DECAY (alte Werte abschwächen)
    # -------------------------------------------------

    for k in learning[action][key]:
        learning[action][key][k] *= DECAY_FACTOR

    # --- SAFE UPDATE ---
    if result == "GOOD":
        learning[action][key]["GOOD"] += 1.0
    elif result == "BAD":
        learning[action][key]["BAD"] += 1.0
    else:
        learning[action][key]["NEUTRAL"] += 1.0


# ============================================================
# SCORE BERECHNUNG
# ------------------------------------------------------------
# Gibt Score für Action im aktuellen Kontext zurück
# ============================================================

def get_action_score(action, context=None, runtime=None):

    action = str(action).upper()

    # --- Fallbacks für alte Aufrufe ---
    if runtime is None:
        return 0.0

    key = build_context_key(runtime=runtime)

    stats = learning.get(action, {}).get(key, {})

    good = stats.get("GOOD", 0.0)
    bad = stats.get("BAD", 0.0)

    total = good + bad

    if total == 0:
        return 0.0

    # -------------------------------------------------
    # MIN SAMPLES PROTECTION
    # -------------------------------------------------

    if total < MIN_SAMPLES:
        return 0.0

    # -------------------------------------------------
    # SCORE
    # -------------------------------------------------

    raw_score = (good - bad) / total

    # clamp
    if raw_score > MAX_SCORE:
        return MAX_SCORE

    if raw_score < -MAX_SCORE:
        return -MAX_SCORE

    return raw_score


# ============================================================
# DEBUG / OBSERVABILITY
# ============================================================

def get_action_stats(action):
    action = str(action).upper()
    return learning.get(action, {})


def get_learning_state():
    return learning
