from dataclasses import dataclass
from typing import Any, Dict, Optional
import time
import uuid


@dataclass
class Decision:
    decision_id: str
    timestamp: float

    decision_type: str  # "normal" | "none"

    trigger_signal: Dict[str, Any]
    signal_context: Dict[str, Any]

    runtime_state_snapshot: Dict[str, Any]

    reasoning: str
    confidence: float
    priority: int

    meta: Dict[str, Any]  # active, required, missing

    recommended_action: Optional[str] = None


def create_decision(
    trigger_signal,
    context,
    runtime_state,
    reasoning,
    confidence,
    priority,
    action=None,
    decision_type="normal",
    meta=None
):
    return Decision(
        decision_id=str(uuid.uuid4()),
        timestamp=time.time(),

        decision_type=decision_type,

        trigger_signal=trigger_signal,
        signal_context=context,
        runtime_state_snapshot=runtime_state,

        reasoning=reasoning,
        confidence=confidence,
        priority=priority,

        meta=meta or {},

        recommended_action=action
    )
