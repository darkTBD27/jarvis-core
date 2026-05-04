import time

learning_runtime = {}

COOLDOWN_SECONDS = 5
MAX_DELTA_PER_UPDATE = 0.02


def get_confidence_adjustment(action, context=None, runtime=None):
    return 0.0


def get_priority_adjustment(action, context=None, runtime=None):
    return 0.0
