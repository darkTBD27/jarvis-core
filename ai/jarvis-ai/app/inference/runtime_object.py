import time


class RuntimeState:

    def __init__(self):

        self.inference_start = None

        self.state = "idle" 

        self.busy = False

        self.current_request = None

        self.started = False

        self.start_time = time.time()

        self.metrics = {

            "requests_total":0,
            "requests_success":0,
            "requests_error":0,
            "requests_timeout":0,

            "queue_processed":0,
            "priority_requests":0,
            "slow_requests":0,

            "total_duration":0,
            "avg_duration":0,

            "last_duration":0,
            "tokens_per_sec":0,
            "tokens_last":0,

            "last_success_request":None

        }

        self.health = "unknown"

        self.queue_size = 0

        self.history = []

        self.worker_heartbeat = time.time()

        self.worker_last_activity = time.time()

        self.worker_status = "starting"

        self.MAX_HISTORY = 100

        self.signal_history = []

        self.MAX_SIGNAL_HISTORY = 100

        self.last_request = None

        self.last_error = None

        self.error_types = {}

        self.health_history = []

        self.MAX_HEALTH_HISTORY = 50


    def set_state(self,state):

        self.state = state


    def set_busy(self,value):

        self.busy = value


    def set_health(self,state):

        self.health_state = state


    def get_health(self):

        return self.health


    def is_busy(self):

        return self.busy


    def set_current(self,request_id):

        self.current_request = request_id


    def clear_current(self):

        self.current_request = None


    def metric_inc(self,name):

        if name not in self.metrics:

            self.metrics[name] = 0

        self.metrics[name] += 1


    def metric_set(self,name,value):

        self.metrics[name] = value


    def metric_get(self,name):

        return self.metrics.get(name,0)


    def add_history(self,entry):

        if len(self.history) >= self.MAX_HISTORY:

            self.history.pop(0)

        self.history.append(entry)


    def get_worker_status(self):

        now = time.time()

        if now - self.worker_heartbeat > 10:

            return "stalled"

        if self.busy:

            return "processing"

        return "idle"


    def get_worker_heartbeat_age(self):

        return time.time() - self.worker_heartbeat


    def get_worker_last_activity_age(self):

        return time.time() - self.worker_last_activity


    def get_uptime(self):

        return int(time.time() - self.start_time)


    def check_worker_health(self):

        now = time.time()

        if now - self.worker_heartbeat > 10:

            self.health_state = "degraded"

            return "stalled"

        return "ok"


    def get_last_error(self):

        from inference.runtime_errors import get_last_error

        return get_last_error()


    def get_error_types(self):

        from inference.runtime_errors import get_error_types

        return get_error_types()


    def get_error_history(self):

        from inference.runtime_errors import get_error_history

        return get_error_history()


    def get_runtime_events(self):

        from inference.runtime_state import get_runtime_events

        return get_runtime_events()


    def add_health_history(self,state):

        if len(self.health_history) >= self.MAX_HEALTH_HISTORY:

            self.health_history.pop(0)

        self.health_history.append({

            "state":state,

            "time":time.time()

        })


    def get_health_history(self):

        return self.health_history


    def add_signal_history(self, signals):

        import time

        entry = {

            "signals": signals,
            "time": time.time()

        }

        if len(self.signal_history) >= self.MAX_SIGNAL_HISTORY:

            self.signal_history.pop(0)

        self.signal_history.append(entry)


RUNTIME = RuntimeState()


def get_runtime():

    return RUNTIME
