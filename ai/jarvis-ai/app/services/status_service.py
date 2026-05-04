# VERIFY MARKER: !3T§!$(a

from inference.runtime_state import get_request_event_flow
from inference.runtime_state import get_runtime_snapshot

EXPECTED_RUNTIME_FLOW = [
    "runtime_run_requested",
    "queue_enqueue",
    "queue_dequeue",
    "request_started",
    "execution_started",
    "execution_finished",
    "decision_made",
    "action_executed",
    "runtime_idle"
]


def get_status():
    return get_runtime_snapshot()


def get_request_flow(request_id):
    return {
        "request_id": request_id,
        "events": get_request_event_flow(request_id)
    }


def compare_request_flow(request_id):
    flow = get_request_event_flow(request_id)

    observed = [event.get("type") for event in flow]

    missing = [step for step in EXPECTED_RUNTIME_FLOW if step not in observed]
    unexpected = [step for step in observed if step not in EXPECTED_RUNTIME_FLOW]

    ordered = observed == sorted(
        observed,
        key=lambda step: EXPECTED_RUNTIME_FLOW.index(step)
        if step in EXPECTED_RUNTIME_FLOW else 999
    )

    return {
        "request_id": request_id,
        "expected": EXPECTED_RUNTIME_FLOW,
        "observed": observed,
        "missing": missing,
        "unexpected": unexpected,
        "ordered": ordered,
        "valid": len(missing) == 0 and len(unexpected) == 0 and ordered
    }


def classify_architecture_relevance(request_id):
    result = compare_request_flow(request_id)

    if result["valid"]:
        classification = "irrelevant"
        backbone_rule = "none"

    elif result["missing"] and not result["unexpected"]:
        classification = "structural_risk"
        backbone_rule = "runtime_flow"

    elif result["unexpected"] and not result["missing"]:
        classification = "observability_gap"
        backbone_rule = "observability_integrity"

    elif not result["ordered"]:
        classification = "backbone_violation"
        backbone_rule = "execution_isolation"

    else:
        classification = "tolerable_deviation"
        backbone_rule = "runtime_flow"

    return {
        "request_id": request_id,
        "valid": result["valid"],
        "classification": classification,
        "backbone_rule": backbone_rule,
        "details": {
            "missing": result["missing"],
            "unexpected": result["unexpected"],
            "ordered": result["ordered"]
        }
    }


def filter_operational_relevance(request_id):
    result = classify_architecture_relevance(request_id)

    if result["classification"] == "irrelevant":
        action = "ignore"

    elif result["classification"] == "tolerable_deviation":
        action = "observe"

    elif result["classification"] == "observability_gap":
        action = "revalidate"

    elif result["classification"] in ("structural_risk", "backbone_violation"):
        action = "operate"

    else:
        action = "observe"

    return {
        "request_id": request_id,
        "valid": result["valid"],
        "classification": result["classification"],
        "backbone_rule": result["backbone_rule"],
        "action": action,
        "details": result["details"]
    }


def prioritize_risk(request_id):
    result = filter_operational_relevance(request_id)

    if result["action"] == "operate":
        priority = "high"

    elif result["action"] == "revalidate":
        priority = "medium"

    elif result["action"] == "observe":
        priority = "low"

    else:
        priority = "none"

    return {
        "request_id": request_id,
        "valid": result["valid"],
        "classification": result["classification"],
        "backbone_rule": result["backbone_rule"],
        "action": result["action"],
        "priority": priority,
        "details": result["details"]
    }


def isolate_next_task(request_id):
    result = prioritize_risk(request_id)

    if result["priority"] == "high":
        next_task = "new_current_task"

    elif result["priority"] == "medium":
        next_task = "revalidate_later"

    elif result["priority"] == "low":
        next_task = "observe_only"

    else:
        next_task = "none"

    return {
        "request_id": request_id,
        "valid": result["valid"],
        "classification": result["classification"],
        "backbone_rule": result["backbone_rule"],
        "action": result["action"],
        "priority": result["priority"],
        "next_task": next_task,
        "details": result["details"]
    }


def validate_backbone_gate(request_id):
    result = isolate_next_task(request_id)

    gate_passed = (
        result["valid"] or
        result["next_task"] in ("new_current_task", "revalidate_later", "observe_only", "none")
    )

    return {
        "request_id": request_id,
        "valid": result["valid"],
        "classification": result["classification"],
        "backbone_rule": result["backbone_rule"],
        "action": result["action"],
        "priority": result["priority"],
        "next_task": result["next_task"],
        "gate_passed": gate_passed,
        "details": result["details"]
    }


def build_validation_pipeline(request_id):
    return validate_backbone_gate(request_id)
