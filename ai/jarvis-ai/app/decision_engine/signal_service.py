from inference.runtime_object import get_runtime


def get_latest_signals(limit=5):
    runtime = get_runtime()

    history = getattr(runtime, "signal_history", [])

    if not history:
        return []

    return history[-limit:]


def get_last_signal():
    signals = get_latest_signals(1)

    if not signals:
        return None

    return signals[0]
