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

def build_context_key(outcome):

    queue = outcome.context.get("queue_before", 0)

    if queue == 0:
        return "queue_0"

    if queue < 3:
        return "queue_low"

    if queue < 6:
        return "queue_medium"

    return "queue_high"


# ============================================================
# UPDATE LEARNING
# ------------------------------------------------------------
# Speichert Ergebnis einer Action im Kontext
# ============================================================

def update_learning(action, result, outcome):

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

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    if result not in learning[action][key]:
        learning[action][key][result] = 0.0

    learning[action][key][result] += 1.0


# ============================================================
# SCORE BERECHNUNG
# ------------------------------------------------------------
# Gibt Score für Action im aktuellen Kontext zurück
# ============================================================

def get_action_score(action, context=None, runtime=None):

    # --- Fallbacks für alte Aufrufe ---
    if runtime is None:
        return 0.0

    queue = runtime.queue_size

    if queue == 0:
        key = "queue_0"
    elif queue < 3:
        key = "queue_low"
    elif queue < 6:
        key = "queue_medium"
    else:
        key = "queue_high"

    stats = learning.get(action, {}).get(key, {})

    good = stats.get("GOOD", 0.0)
    bad = stats.get("BAD", 0.0)

    total = good + bad

    if total == 0:
        return 0.0

    return (good - bad) / total

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
    return learning.get(action, {})


def get_learning_state():
    return learning
