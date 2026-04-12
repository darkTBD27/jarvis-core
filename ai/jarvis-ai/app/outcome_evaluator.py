def evaluate_outcome(outcome):
    """
    Bewertet ein RuntimeOutcome.
    
    Rückgabe:
    - "GOOD"
    - "BAD"
    - "NEUTRAL"
    """

    # -------------------------
    # 1. Harte Fehler
    # -------------------------
    if not outcome.success:
        return "BAD"

    # -------------------------
    # 2. Performance Problem
    # -------------------------
    if outcome.execution_time > 5:
        return "BAD"

    # -------------------------
    # 3. Queue Verbesserung
    # -------------------------
    if outcome.queue_after < outcome.queue_before:
        return "GOOD"

    # -------------------------
    # 4. Worker Stabilität
    # -------------------------
    if outcome.worker_after >= outcome.worker_before:
        return "GOOD"

    # -------------------------
    # 5. Default
    # -------------------------
    return "NEUTRAL"
