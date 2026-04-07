from inference.queue_system import dequeue_request
from inference.queue_system import queue_empty
from inference.queue_system import queue_size

from inference.inference import run_inference

from inference.runtime_object import get_runtime
from inference.runtime_health import calculate_health
from inference.runtime_automation import run_automation
from inference.runtime_automation import check_runtime_triggers
from inference.worker_config import get_worker_config
from inference.runtime_state import add_runtime_event
from inference.runtime_errors import add_error

from inference.reasoning.reasoning_engine import ReasoningEngine

import time
import traceback


WORKER_IDLE_SLEEP = get_worker_config("worker_idle_sleep")


class RuntimeWorker:

    def __init__(self):

        self.running = False
        self.runtime = get_runtime()
        self.reasoning = ReasoningEngine()


    def start(self):

        if self.running:
            return

        self.running = True

        self.runtime.set_state("starting")
        self.runtime.started = True

        self.runtime.worker_status = "running"


        while self.running:

            try:

                self.runtime.worker_heartbeat = time.time()

                self.runtime.queue_size = queue_size()

                health = calculate_health()

                if self.runtime.check_worker_health() == "stalled":

                    self.runtime.metric_inc("worker_stalls")

                    self.runtime.set_health("degraded")


                self.reasoning.cycle()

                triggers = check_runtime_triggers()
                run_automation(triggers)


                if queue_empty():

                    self.runtime.set_state("idle")

                    self.runtime.worker_status = "idle"

                    time.sleep(WORKER_IDLE_SLEEP)

                    continue


                item = dequeue_request()

                self.runtime.worker_last_activity = time.time()

                if not item:
                    continue


                priority, payload = item

                self.runtime.metric_inc("queue_processed")

                if priority:
                    self.runtime.metric_inc("priority_requests")


                retry_count = 0
                max_retries = get_worker_config("worker_max_retries")

                prompt = payload[0]
                max_tokens = payload[1]
                temperature = payload[2]
                request_id = payload[3]


                self.runtime.set_state("processing")

                self.runtime.set_current(request_id)

                add_runtime_event(

                    "request_started",

                    {

                        "request_id":request_id

                    }

                )

                self.runtime.set_busy(True)

                self.runtime.worker_status = "processing"

                self.runtime.worker_last_activity = time.time()


                start_exec = time.time()

                self.runtime.inference_start = start_exec


                while retry_count <= max_retries:

                    try:

                        result = run_inference(

                            prompt,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            request_id=request_id,
                            priority=priority

                        )

                        duration = time.time() - start_exec

                        if duration > get_worker_config("slow_request_seconds"):

                            self.runtime.set_health("degraded")

                            self.runtime.metric_inc("slow_requests")

                        break


                    except Exception as e:

                        traceback.print_exc()

                        raise


                self.runtime.inference_start = None

                self.runtime.set_busy(False)

                self.runtime.worker_last_activity = time.time()

                self.runtime.clear_current()

                self.runtime.worker_status = "running"


            except Exception as e:

                error_type = type(e).__name__

                add_error(error_type)

                self.runtime.set_state("error")

                self.runtime.worker_status = "error"

                self.runtime.metric_inc("worker_errors")
                self.runtime.metric_inc(f"worker_error_{error_type}")

                traceback.print_exc()

                time.sleep(
                    get_worker_config("worker_error_sleep")
                )


    def stop(self):

        self.running = False

        self.runtime.set_state("stopped")

        self.runtime.clear_current()

        self.runtime.set_busy(False)
