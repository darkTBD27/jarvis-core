from inference.queue_system import dequeue_request, queue_empty, queue_size
from inference.inference import run_inference

from inference.runtime_object import get_runtime
from inference.runtime_health import calculate_health
from inference.runtime_automation import run_automation, check_runtime_triggers
from inference.worker_config import get_worker_config
from inference.runtime_state import add_runtime_event
from inference.runtime_errors import add_error
from inference.runtime_intelligence import get_runtime_intelligence

from inference.reasoning.reasoning_engine import ReasoningEngine

from decision_engine.decision_builder import build_decision
from decision_engine.signal_service import get_latest_signals
from decision_engine.action_mapper import map_decision_to_action
from decision_engine.action_executor import execute_action

from inference.inference_lock import inference_lock


import time
import traceback
import logging
import threading
import logging


# --- WORKER CONTROL ---
worker_threads = []  # [(thread, control_flag)]
worker_target_count = 1
MAX_WORKERS = 3


logger = logging.getLogger("jarvis")


class RuntimeWorker:

    def __init__(self):
        self.running = False
        self.runtime = get_runtime()
        self.reasoning = ReasoningEngine()

        self.idle_sleep = get_worker_config("worker_idle_sleep")

        self.error_count = 0
        self.last_error_time = None

    # -------------------------
    # WORKER THREAD LOOP
    # -------------------------
    def worker_loop(self, control):

        while self.running and control["active"]:
            try:
                self._worker_cycle()

            except Exception as e:
                error_type = type(e).__name__

                add_error(error_type)

                self.runtime.set_state("error")
                self.runtime.worker_status = "error"

                self.runtime.metric_inc("worker_errors")
                self.runtime.metric_inc(f"worker_error_{error_type}")

                logger.exception("Worker Error")

                # --- ERROR TRACKING ---
                now = time.time()

                if self.last_error_time and (now - self.last_error_time < 10):
                    self.error_count += 1
                else:
                    self.error_count = 1

                self.last_error_time = now

                # --- BACKOFF ---
                sleep_time = min(5 * self.error_count, 30)

                logger.warning(f"[WORKER] error_backoff count={self.error_count} sleep={sleep_time}s")

                time.sleep(sleep_time)

    # -------------------------
    # SINGLE CYCLE
    # -------------------------
    def _worker_cycle(self):

        self.runtime.worker_heartbeat = time.time()
        current_queue_size = queue_size()
        self.runtime.queue_size = current_queue_size

        calculate_health()

        if self.runtime.check_worker_health() == "stalled":
            self.runtime.metric_inc("worker_stalls")
            self.runtime.set_health("degraded")

        self.reasoning.cycle()

        triggers = check_runtime_triggers()
        run_automation(triggers)

        # --- IDLE ---
        if queue_empty():
            self.runtime.set_state("idle")
            self.runtime.worker_status = "idle"
            time.sleep(self.idle_sleep)
            return

        # --- DEQUEUE ---
        item = dequeue_request()

        self.runtime.worker_last_activity = time.time()

        if not item:
            return

        priority, payload = item

        self.runtime.metric_inc("queue_processed")

        if priority:
            self.runtime.metric_inc("priority_requests")

        prompt, max_tokens, temperature, request_id = payload

        self.runtime.set_state("processing")
        self.runtime.set_current(request_id)

        add_runtime_event("request_started", {"request_id": request_id})

        self.runtime.set_busy(True)
        self.runtime.worker_status = "processing"

        start_exec = time.time()
        self.runtime.inference_start = start_exec

        # --- INFERENCE ---
        try:
            with inference_lock:
                run_inference(
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

        except Exception:
            logger.exception("Inference Error")
            raise

        # --- CLEANUP ---
        self.runtime.inference_start = None
        self.runtime.set_busy(False)
        self.runtime.worker_last_activity = time.time()
        self.runtime.clear_current()
        self.runtime.worker_status = "running"

        logger.warning("HOOK REACHED")

        # --- INTELLIGENCE ---
        try:
            get_runtime_intelligence()
        except Exception:
            pass

        # --- DECISION + ACTION ---
        try:
            signals = get_latest_signals()
            logger.warning(f"SIGNALS IN WORKER: {signals}")

            decision = build_decision()
            logger.warning(f"DECISION RAW: {decision}")

            if decision:
                logger.warning(f"[DECISION] {decision}")

                action = map_decision_to_action(decision)

                if action:
                    logger.warning(f"[ACTION] {action}")
                    execute_action(action)

        except Exception as e:
            logger.warning(f"[DECISION ERROR] {e}")

    # -------------------------
    # START SYSTEM
    # -------------------------
    def start(self):

        if self.running:
            return

        self.running = True

        self.runtime.set_state("starting")
        self.runtime.started = True
        self.runtime.worker_status = "running"

        logger.info("[WORKER] started")
        logger.info("[WORKER] processing")
        logger.info("[WORKER] idle")

        for _ in range(worker_target_count):
            self.start_worker_thread()

    # -------------------------
    # START SINGLE THREAD
    # -------------------------
    def start_worker_thread(self):

        control = {"active": True}

        t = threading.Thread(
            target=self.worker_loop,
            args=(control,),
            daemon=True
        )

        t.start()

        worker_threads.append((t, control))

    # -------------------------
    # SCALE UP
    # -------------------------
    def scale_workers(self):

        global worker_target_count

        if worker_target_count >= MAX_WORKERS:
            logger.warning("[WORKER] max workers reached")
            return

        worker_target_count += 1

        logger.warning(f"[WORKER] scaling up → {worker_target_count}")

        self.start_worker_thread()

    # -------------------------
    # SCALE DOWN
    # -------------------------
    def scale_down(self):

        global worker_target_count

        if worker_target_count <= 1:
            logger.warning("[WORKER] already at minimum")
            return

        worker_target_count -= 1

        logger.warning(f"[WORKER] scaling down → {worker_target_count}")

        if worker_threads:
            thread, control = worker_threads.pop()
            control["active"] = False

    # -------------------------
    # STOP
    # -------------------------
    def stop(self):

        self.running = False

        self.runtime.set_state("stopped")
        self.runtime.clear_current()
        self.runtime.set_busy(False)
