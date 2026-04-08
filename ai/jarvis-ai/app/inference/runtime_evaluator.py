from inference.runtime_state import get_runtime
import time


def evaluate_runtime():

    runtime = get_runtime()

    evaluation = {

        "health":runtime.get_health(),

        "worker_status":runtime.get_worker_status(),

        "heartbeat_age":runtime.get_worker_heartbeat_age(),

        "last_activity_age":runtime.get_worker_last_activity_age(),

        "queue_size":runtime.queue_size,

        "error_count":len(runtime.get_error_history()),

        "error_types":runtime.get_error_types(),

        "uptime":runtime.get_uptime(),

        "busy":runtime.is_busy()

    }

    return evaluation
