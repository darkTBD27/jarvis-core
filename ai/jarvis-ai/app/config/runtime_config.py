import os


# ========================
# QUEUE
# ========================

MAX_QUEUE_SIZE = int(
    os.getenv("LLM_MAX_QUEUE", 10)
)


# ========================
# REQUEST LIMITS
# ========================

MAX_REQUESTS_PER_WINDOW = int(
    os.getenv("LLM_RATE_LIMIT", 20)
)

RATE_WINDOW = int(
    os.getenv("LLM_RATE_WINDOW", 10)
)


# ========================
# MODEL EXECUTION
# ========================

LLM_TIMEOUT = int(
    os.getenv("LLM_TIMEOUT", 60)
)

LLM_MAX_TOKENS = int(
    os.getenv("LLM_MAX_TOKENS", 200)
)

LLM_TEMP = float(
    os.getenv("LLM_TEMP", 0.7)
)


# ========================
# HISTORY
# ========================

MAX_REQUEST_HISTORY = int(
    os.getenv("REQUEST_HISTORY_LIMIT", 100)
)


# ========================
# HEALTH
# ========================

HEALTH_ERROR_THRESHOLD = 0.25

HEALTH_DEGRADED_ERROR_THRESHOLD = 0.10

HEALTH_TIMEOUT_THRESHOLD = 0.15

HEALTH_QUEUE_BUSY = 5


# ========================
# CONFIG INTERFACES
# ========================

def get_health_config():

    return {

        "error": HEALTH_ERROR_THRESHOLD,

        "degraded_error": HEALTH_DEGRADED_ERROR_THRESHOLD,

        "timeout": HEALTH_TIMEOUT_THRESHOLD,

        "queue_busy": HEALTH_QUEUE_BUSY

    }


def get_runtime_limits():

    return {

        "queue": MAX_QUEUE_SIZE,

        "rate_limit": MAX_REQUESTS_PER_WINDOW,

        "rate_window": RATE_WINDOW,

        "timeout": LLM_TIMEOUT,

        "max_tokens": LLM_MAX_TOKENS,

        "temperature": LLM_TEMP

    }


DEFAULT_SYSTEM_PROMPT = """
Du bist Jarvis.
Du antwortest immer auf Deutsch.
Du antwortest klar, technisch präzise und hilfreich.
Wenn es um Systeme geht denkst du wie ein Operator.
"""
