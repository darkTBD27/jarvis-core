# ============================================================
# RUNTIME OUTCOME
# ------------------------------------------------------------
# Zweck:
# Speichert das Ergebnis einer Action-Ausführung
#
# Wichtig:
# Outcome ist die Grundlage für Learning
#
# Enthält:
# - Action
# - Erfolg / Fehler
# - Timing
# - Systemzustand vorher/nachher
# - Kontext
# ============================================================

import time
from dataclasses import dataclass, asdict


# ============================================================
# DATA STRUCTURE
# ============================================================

@dataclass
class RuntimeOutcome:
    request_id: str
    decision_id: str
    action_type: str

    timestamp_start: float
    timestamp_end: float

    success: bool
    error_type: str | None

    execution_time: float

    queue_before: int
    queue_after: int

    worker_before: str
    worker_after: str

    system_state_hash: str

    # Phase 5.4 – Kontext für Learning
    context: dict


    def to_dict(self):
        return asdict(self)


# ============================================================
# FACTORY
# ------------------------------------------------------------
# Einheitliche Erstellung eines Outcomes
# Wichtig für Konsistenz im System
# ============================================================

def create_outcome(
    request_id: str,
    decision_id: str,
    action_type: str,
    start_time: float,
    success: bool,
    error_type: str | None,
    queue_before: int,
    queue_after: int,
    worker_before: str,
    worker_after: str,
    system_state_hash: str,
):

    end_time = time.time()

    # -------------------------------------------------
    # CONTEXT (Phase 5.4)
    # -------------------------------------------------

    context = {
        "queue_before": queue_before,
        "queue_after": queue_after,
        "worker_before": worker_before,
        "worker_after": worker_after
    }

    return RuntimeOutcome(
        request_id=request_id,
        decision_id=decision_id,
        action_type=action_type,

        timestamp_start=start_time,
        timestamp_end=end_time,

        success=success,
        error_type=error_type,

        execution_time=end_time - start_time,

        queue_before=queue_before,
        queue_after=queue_after,

        worker_before=worker_before,
        worker_after=worker_after,

        system_state_hash=system_state_hash,

        context=context
    )
