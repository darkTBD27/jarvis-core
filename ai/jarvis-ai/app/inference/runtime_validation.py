import time
from typing import Any, Dict, List, Optional

STATUS_OK = "OK"
STATUS_BROKEN = "BROKEN"
STATUS_INCOMPLETE = "INCOMPLETE"

STATUS_PRIORITY = {
    STATUS_OK: 0,
    STATUS_INCOMPLETE: 1,
    STATUS_BROKEN: 2,
}

MANDATORY_CHECKPOINTS = (
    "closure_checkpoint_seen",
    "finalize_checkpoint_seen",
    "snapshot_checkpoint_seen",
    "forced_close_checkpoint_seen",
)

CONDITIONAL_CHECKPOINTS = (
    "snapshot_entered",
    "snapshot_committed",
    "forced_closed",
)

def _empty_validation_state() -> Dict[str, Any]:
    return {
        "cycle_id": None,
        "closure_checkpoint_seen": False,
        "finalize_checkpoint_seen": False,
        "snapshot_checkpoint_seen": False,
        "snapshot_entered": False,
        "snapshot_committed": False,
        "forced_close_checkpoint_seen": False,
        "forced_closed": False,
        "checkpoint_total": 0,
        "checkpoint_completed": 0,
        "checkpoint_failed": 0,
        "final_validation_status": None,
        "final_validation_reason": None,
        "validation_completed_at": None,
    }

def build_validation_state(cycle_id: Optional[str] = None) -> Dict[str, Any]:
    state = _empty_validation_state()
    state["cycle_id"] = cycle_id
    return state

def evaluate_runtime_validation(validation: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    state = _empty_validation_state()
    state.update(dict(validation or {}))
    violations: List[str] = []

    def add_violation(reason: str) -> None:
        violations.append(reason)

    def set_terminal(status: str, reason: str) -> None:
        current = state["final_validation_status"]
        if current is None or STATUS_PRIORITY[status] > STATUS_PRIORITY.get(current, -1):
            state["final_validation_status"] = status
            state["final_validation_reason"] = reason

    if state["cycle_id"] is None:
        set_terminal(STATUS_INCOMPLETE, "missing_cycle_identity")

    for checkpoint in MANDATORY_CHECKPOINTS:
        if not state.get(checkpoint, False):
            add_violation(f"missing_{checkpoint}")
            set_terminal(STATUS_BROKEN, f"missing_{checkpoint}")

    if state["snapshot_entered"] and not state["snapshot_committed"]:
        add_violation("snapshot_commit_missing")
        set_terminal(STATUS_BROKEN, "snapshot_commit_missing")

    if not state["snapshot_entered"] and state["snapshot_committed"]:
        add_violation("snapshot_commit_without_entry")
        set_terminal(STATUS_BROKEN, "snapshot_commit_without_entry")

    if state["forced_closed"]:
        add_violation("forced_cycle_close")
        set_terminal(STATUS_BROKEN, "forced_cycle_close")

    checkpoint_total = len(MANDATORY_CHECKPOINTS)
    if state["snapshot_entered"]: checkpoint_total += 1
    if state["snapshot_committed"]: checkpoint_total += 1
    if state["forced_closed"]: checkpoint_total += 1

    checkpoint_completed = sum(1 for cp in MANDATORY_CHECKPOINTS if state.get(cp, False))
    checkpoint_completed += sum(1 for cp in CONDITIONAL_CHECKPOINTS if state.get(cp, False))

    state["checkpoint_total"] = checkpoint_total
    state["checkpoint_completed"] = checkpoint_completed
    state["checkpoint_failed"] = len(violations)

    if state["checkpoint_failed"] > 0:
        set_terminal(STATUS_BROKEN, state["final_validation_reason"] or "failed_checkpoint_chain")

    if checkpoint_completed < checkpoint_total and state["final_validation_status"] != STATUS_BROKEN:
        set_terminal(STATUS_INCOMPLETE, "incomplete_checkpoint_chain")

    if (
        checkpoint_completed == checkpoint_total
        and state["checkpoint_failed"] == 0
        and not state["forced_closed"]
        and state["snapshot_entered"] == state["snapshot_committed"]
    ):
        set_terminal(STATUS_OK, "validation_complete")

    state["validation_completed_at"] = time.time()
    return state


def mark_checkpoint(state: Dict[str, Any], checkpoint: str):
    """Setzt einen Checkpoint im Validierungs-State."""
    if checkpoint in state:
        state[checkpoint] = True
        # Erzeugt automatisch einen Timestamp-Key (z.B. finalize_checkpoint_seen_at)
        state[f"{checkpoint}_at"] = time.time()
