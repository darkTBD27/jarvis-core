#VERIFY MARKER: B79J)+.,

from inference.runtime_object import RUNTIME_ACCESS


def get_latest_signals(limit=5):

    history = RUNTIME_ACCESS.read("signals")

    if not history:
        return []

    return history[-limit:]


def get_last_signal():
    signals = get_latest_signals(1)

    if not signals:
        return None

    return signals[0]
