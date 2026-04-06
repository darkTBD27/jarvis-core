CONFIG = {

    "worker_idle_sleep":0.05,

    "slow_request_seconds":10,

    "worker_max_retries":1,

    "retry_delay":0.1,

    "worker_error_sleep":0.5,

    "health_queue_degraded":5,

    "health_queue_critical":10

}


def get_config(name,default=None):

    return CONFIG.get(name,default)
