from decision_engine.signal_service import get_latest_signals
from decision_engine.decision_object import create_decision

from inference.runtime_state import get_runtime_snapshot


def build_decision():

    runtime_state = get_runtime_snapshot()

    # --- FIX ---
    # erzwinge dict + entferne kaputte Attribut-Zugriffe
    if hasattr(runtime_state, "__dict__"):
        runtime_state = vars(runtime_state)
    elif not isinstance(runtime_state, dict):
        runtime_state = {}

    signals = get_latest_signals()

    if not signals:
        return None

    # letzter Signal-Eintrag
    latest_entry = signals[-1]

    raw_signals = latest_entry.get("signals", [])

    if not raw_signals:
        return None

    valid_signals = [s for s in raw_signals if isinstance(s, dict)]

    if not valid_signals:
        return None

    trigger_signal = valid_signals[-1]
    signal_types = [s.get("type") for s in valid_signals]

    confidence = 0.5
    priority = 1

    context = {
        "recent_signal_entries": signals
    }

    # --- Bewertung (minimal stabil) ---
    reasoning = "Initial decision based on runtime signal"
    confidence = 0.5
    priority = 1

    if "RUNTIME_INSTABILITY" in signal_types:
        reasoning = "Critical instability detected"
        confidence = 0.95
        priority = 10

    elif "RUNTIME_RISK_HIGH" in signal_types:
        reasoning = "High runtime risk"
        confidence = 0.85
        priority = 8

    elif "QUEUE_PRESSURE" in signal_types:
        reasoning = "Queue pressure detected"
        confidence = 0.7
        priority = 6

    elif "WORKER_STALLED" in signal_types:
        reasoning = "Worker stalled"
        confidence = 0.9
        priority = 9

    elif "RUNTIME_IDLE" in signal_types:
        reasoning = "System idle"
        confidence = 0.6
        priority = 3

    return create_decision(
        trigger_signal=trigger_signal,
        context=context,
        runtime_state=runtime_state,
        reasoning=reasoning,
        confidence=confidence,
        priority=priority,
        action=None
    )


def run_test():
    print("TEST START")

    signals = get_latest_signals()
    print("RAW SIGNALS:", signals)

    decision = build_decision()
    print("DECISION:", decision)

    from inference.runtime_object import get_runtime

    rt = get_runtime()
    print("RUNTIME ID:", id(rt))
    print("SIGNAL HISTORY DIRECT:", rt.signal_history)


if __name__ == "__main__":
    run_test()
