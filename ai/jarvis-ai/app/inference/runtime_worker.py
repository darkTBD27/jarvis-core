# VERIFY_MARKER: A7F3-01

from inference.queue_system import dequeue_request, queue_empty, queue_size
from inference.inference import run_inference

from engine.logger import logger

from inference.runtime_object import RUNTIME_ACCESS
from inference.runtime_health import calculate_health
from inference.runtime_automation import run_automation, check_runtime_triggers
from inference.worker_config import get_worker_config

from inference.runtime_errors import add_error
from inference.runtime_intelligence import get_runtime_intelligence
from inference.runtime_validation import evaluate_runtime_validation, build_validation_state, mark_checkpoint

def set_runtime_context(phase, key, value):
    ctx = RUNTIME_ACCESS.read("runtime_context")

    updated = dict(ctx)
    updated[key] = {
        "value": value,
        "phase": phase,
        "time": time.time()
    }

    RUNTIME_ACCESS.write("runtime_context", updated)

from inference.reasoning.reasoning_engine import ReasoningEngine

from decision_engine.decision_builder import build_decision
from decision_engine.signal_service import get_latest_signals
from decision_engine.action_mapper import map_decision_to_action
from decision_engine.action_executor import execute_action

from inference.inference_lock import inference_lock

from inference.runtime_outcome import create_outcome
from outcome_evaluator import evaluate_outcome
from learning_store import update_learning, get_action_stats


import time
import threading


MAX_WORKERS = 3

ACTION_WEIGHT_THRESHOLD = 2.5
ACTION_CONFIDENCE_THRESHOLD = 0.6
ACTION_PRIORITY_THRESHOLD = 3

ACTION_COOLDOWN_SECONDS = 5


CONTEXT_PHASE_REQUEST_START = "REQUEST_START"
CONTEXT_PHASE_POST_EXECUTION = "POST_EXECUTION"
CONTEXT_PHASE_POST_ACTION = "POST_ACTION"

ALLOWED_CONTEXT_WRITES = {
    CONTEXT_PHASE_REQUEST_START: [
        "current_request_id",
    ],
    CONTEXT_PHASE_POST_EXECUTION: [
        "last_request_id",
        "last_execution_time",
    ],
    CONTEXT_PHASE_POST_ACTION: [
        "last_action",
        "last_result",
    ],
}


class RuntimeWorker:

    def __init__(self):

        self.runtime = RUNTIME_ACCESS
        self.runtime.write("started", False)

        logger.warning("### RUNTIME WORKER FILE LOADED ###")

        logger.warning(f"WORKER RUNTIME ID: {id(self.runtime)}")
        logger.warning(f"WORKER MODULE: {self.runtime.__class__.__module__}")
        
        self.reasoning = ReasoningEngine()

        self.idle_sleep = get_worker_config("worker_idle_sleep")


    def worker_loop(self):
        while self.runtime.read("started"):
            cycle_id = f"cyc_{int(time.time() * 1000)}"
            v_state = build_validation_state(cycle_id) 

            current_sys_state = self.runtime.read("state")
            logger.debug(f"[TEST] State Transition Check: {current_sys_state} -> processing")
            
            try:
                if self.runtime.read("state") == "starting":
                    self.runtime.write("state", "idle")

                self.runtime.write("state", "processing")
                self.runtime.write("cycle_id", cycle_id)
                self.runtime.write("cycle_start_ts", time.time())
                self.runtime.write("cycle_finalized", False)

                self._worker_cycle(v_state)

                mark_checkpoint(v_state, "closure_checkpoint_seen")
                evaluate_runtime_validation(v_state)

                self.runtime.write("cycle_end_ts", time.time())
                self.runtime.write("cycle_finalized", True)
                self.runtime.write("worker_status", "idle")

                if self.runtime.read("state") != "idle":
                    self.runtime.write("state", "idle")

                time.sleep(2)

            except Exception as e:
                error_type = type(e).__name__
                add_error(error_type)
                logger.exception(f"[WORKER] Critical Failure in Cycle {cycle_id}")

                v_state["final_validation_status"] = "BROKEN"
                v_state["final_validation_reason"] = f"exception_{error_type}"
                evaluate_runtime_validation(v_state)

                self.runtime.write("cycle_state", "ERROR")
                self.runtime.write("worker_status", "stalled")
                self.runtime.write("cycle_end_ts", time.time())
                self.runtime.write("cycle_finalized", True)
                
                now = time.time()
                last_error_time = self.runtime.read("worker_last_error_time") or 0.0
                error_count = (self.runtime.read("worker_error_count") or 0) + 1
                
                self.runtime.write("worker_error_count", error_count)
                self.runtime.write("worker_last_error_time", now)

                sleep_time = min(5 * error_count, 30)
                logger.warning(f"[WORKER] Emergency Sleep: {sleep_time}s")
                time.sleep(sleep_time)


    def _worker_cycle(self, v_state):

        mark_checkpoint(v_state, "snapshot_checkpoint_seen")

        self.runtime.write("worker_heartbeat", time.time())
        current_queue_size = queue_size()
        self.runtime.write("queue_size", current_queue_size)

        from inference.queue_system import snapshot_queue

        self.runtime.write("queue_snapshot", snapshot_queue())

        calculate_health()

        if self.runtime.read("worker_status") == "stalled":
            self.runtime.write("health", "degraded")

        candidate = self.reasoning.cycle()

        if candidate:
            self.runtime.evaluate_candidate(candidate)

        triggers = check_runtime_triggers()
        run_automation(triggers)

        if queue_empty():
            self.runtime.emit_event("cycle_exit", {
                "cycle_id": None,
                "domain": "exit",
                "reason": "queue_empty"
            })

            was_idle = self.runtime.read("state") == "idle"

            if not was_idle:
                self.runtime.write("state", "idle")
                self.runtime.emit_event("runtime_idle", {})

            self.runtime.write("worker_status", "idle")
            time.sleep(self.idle_sleep)
            return

        item = dequeue_request()

        import uuid

        self.runtime.write("cycle_id", str(uuid.uuid4()))
        self.runtime.write("cycle_start_ts", time.time())
        self.runtime.write("cycle_state", "processing")
        self.runtime.write("cycle_end_ts", None)
        self.runtime.write("cycle_finalized", False)
        self.runtime.write("cycle_persist_failed", False)

        self.runtime.write("snapshot_ts", None)
        self.runtime.write("snapshot_committed", False)

        self.runtime.write("runtime_validation", {
            "cycle_id": self.runtime.read("cycle_id"),
            "closure_checkpoint_seen": False,
            "finalize_checkpoint_seen": False,
            "snapshot_checkpoint_seen": False,
            "snapshot_entered": False,
            "snapshot_committed": False,
            "forced_close_checkpoint_seen": False,
            "forced_closed": False
        })

        self.runtime.write("worker_last_activity", time.time())

        if not item:
            self.runtime.emit_event("cycle_exit", {
                "cycle_id": self.runtime.read("cycle_id"),
                "domain": "exit",
                "reason": "empty_item"
            })
            return

        logger.warning("[DEBUG] worker cycle running")

        priority, payload = item

        prompt, max_tokens, temperature, request_id = payload

        if self.runtime.read("state") != "processing":
            self.runtime.write("state", "processing")
        self.runtime.write("current_request", request_id)

        self.runtime.emit_event("request_started", {"request_id": request_id})

        set_runtime_context(CONTEXT_PHASE_REQUEST_START, "current_request_id", request_id)

        self.runtime.write("busy", True)
        self.runtime.write("worker_status", "processing")

        start_exec = time.time()
        self.runtime.write("inference_start", start_exec)

        try:
            self.runtime.emit_event("execution_started", {"request_id": request_id})

            with inference_lock:
                run_inference(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    request_id=request_id,
                    priority=priority
                )

            duration = time.time() - start_exec

            self.runtime.emit_event("execution_finished", {
                "request_id": request_id,
                "duration": duration
            })

            if duration > get_worker_config("slow_request_seconds"):
                self.runtime.write("health", "degraded")

        except Exception:
            logger.exception("Inference Error")
            raise

        self.runtime.write("inference_start", None)
        self.runtime.write("busy", False)
        self.runtime.write("worker_last_activity", time.time())
        self.runtime.write("current_request", None)
        self.runtime.write("worker_status", "idle")

        set_runtime_context(CONTEXT_PHASE_POST_EXECUTION, "last_request_id", request_id)
        set_runtime_context(CONTEXT_PHASE_POST_EXECUTION, "last_execution_time", duration)

        logger.warning("HOOK REACHED")

        try:
            from inference.signal_pipeline import process_signal

            intelligence = get_runtime_intelligence()
            signals = intelligence.get("signals", [])

            logger.info(f"[WORKER SIGNALS] {signals}")

            snapshot = self.runtime.build_snapshot()
            normalized_signal = process_signal(signals, snapshot)
            decision = build_decision(normalized_signal)

            self.runtime.write("last_decision", decision.to_dict() if decision else {})
            self.runtime.write("decision_history", self.runtime.read("decision_history")[-49:] + [self.runtime.read("last_decision")])

            self.runtime.emit_event("decision_made", {
                "type": decision.decision_type if decision else None
            })

            if decision is None:
                logger.warning("[DECISION ERROR] builder returned None")
                self.runtime.emit_event("cycle_exit", {
                    "cycle_id": self.runtime.read("cycle_id"),
                    "domain": "exit",
                    "reason": "decision_none"
                })
                self._finalize_cycle()
            else:
                logger.warning(f"DECISION RAW: {decision}")
                action = None

                if decision.decision_type == "normal":
                    action = map_decision_to_action(decision)
                    if action:
                        confidence = getattr(decision, "confidence", 0)
                        priority_val = getattr(decision, "priority", 0)
                        weight = (confidence or 0.0) * (priority_val or 0.0)

                        if (
                            weight < ACTION_WEIGHT_THRESHOLD or
                            confidence < ACTION_CONFIDENCE_THRESHOLD or
                            priority_val < ACTION_PRIORITY_THRESHOLD
                        ):
                            logger.info(f"[ACTION BLOCKED] action={action} weight={round(weight,3)}")
                            action = None
                        else:
                            now = time.time()
                            action_times = self.runtime.read("action_last_execution")
                            last_time = action_times.get(action, 0)

                            if now - last_time < ACTION_COOLDOWN_SECONDS:
                                logger.info(f"[COOLDOWN BLOCK] action={action}")
                                action = None
                            else:
                                updated_times = dict(self.runtime.read("action_last_execution"))
                                updated_times[action] = now
                                self.runtime.write("action_last_execution", updated_times)

                if action:
                    start_time = time.time()
                    success = True
                    error_type = None

                    try:
                        execute_action(action)
                    except Exception as e:
                        success = False
                        error_type = type(e).__name__
                        logger.warning(f"[ACTION ERROR] {action} | error={error_type}")

                    self.runtime.emit_event("action_executed", {
                        "action": str(action),
                        "success": success
                    })

                    end_queue = queue_size()
                    outcome = create_outcome(
                        request_id=request_id,
                        decision_id="runtime_decision",
                        action_type=action,
                        start_time=start_time,
                        success=success,
                        error_type=error_type,
                        queue_before=current_queue_size,
                        queue_after=end_queue,
                        worker_before=self.runtime.read("worker_status"),
                        worker_after=self.runtime.read("worker_status"),
                        system_state_hash="na"
                    )

                    self.runtime.write("outcomes", self.runtime.read("outcomes") + [outcome])
                    result = evaluate_outcome(outcome)

                    logger.info(f"[TEST] Learning Check: Action={action} Result={result}")
                    if result is None: logger.error("[TEST_FAIL] Outcome Evaluation returned None")

                    try:
                        update_learning(action, result, outcome)
                    except Exception as e:
                        logger.info(f"[LEARNING UPDATE ERROR] {e}")

                    set_runtime_context(CONTEXT_PHASE_POST_ACTION, "last_action", str(action))
                    set_runtime_context(CONTEXT_PHASE_POST_ACTION, "last_result", result)

        except Exception as e:
            logger.warning(f"[DECISION ERROR] {e}")

        # --- CHECKPOINT CHAIN ---
        self.runtime.emit_event("cycle_closure_checkpoint", {
            "cycle_id": self.runtime.read("cycle_id"),
            "cycle_state": self.runtime.read("cycle_state")
        })

        validation = dict(self.runtime.read("runtime_validation"))
        validation["closure_checkpoint_seen"] = True
        self.runtime.write("runtime_validation", validation)

        mark_checkpoint(v_state, "closure_checkpoint_seen")

        if not self.runtime.read("cycle_finalized"):
            self._finalize_cycle()

        validation = dict(self.runtime.read("runtime_validation"))
        validation["snapshot_checkpoint_seen"] = True
        self.runtime.write("runtime_validation", validation)

        if self.runtime.read("cycle_finalized") and self.runtime.read("snapshot_ts") is None:
            self.runtime.write("worker_status", "idle")
            try:
                self.runtime.emit_event("cycle_snapshot_entered", {
                    "cycle_id": self.runtime.read("cycle_id"),
                    "domain": "snapshot"
                })

                validation = dict(self.runtime.read("runtime_validation"))
                validation["snapshot_entered"] = True
                self.runtime.write("runtime_validation", validation)

                self.runtime.write("snapshot_ts", time.time())
                self.runtime.commit_snapshot(self.runtime.build_snapshot())
                self.runtime.write("snapshot_committed", True)

                validation = dict(self.runtime.read("runtime_validation"))
                validation["snapshot_committed"] = True
                self.runtime.write("runtime_validation", validation)

                self.runtime.emit_event("snapshot_committed", {
                    "cycle_id": self.runtime.read("cycle_id")
                })

            except Exception as e:
                logger.error(f"[SNAPSHOT ERROR] {e}")
                self.runtime.write("cycle_persist_failed", True)

        final_state = self.runtime.read("cycle_state")
        validation = dict(self.runtime.read("runtime_validation"))
        validation["forced_close_checkpoint_seen"] = True
        self.runtime.write("runtime_validation", validation)

        if not self.runtime.read("cycle_finalized") and not self.runtime.read("snapshot_committed") and final_state != "ERROR":
            validation = dict(self.runtime.read("runtime_validation"))
            validation["forced_closed"] = True
            self.runtime.write("runtime_validation", validation)

            self.runtime.write("cycle_state", "ERROR")
            self.runtime.write("cycle_end_ts", time.time())
            self.runtime.write("cycle_finalized", True)

        validation_results = evaluate_runtime_validation(self.runtime.read("runtime_validation"))

        logger.info(
            f"[VALIDATION] status={validation_results['final_validation_status']} "
            f"checkpoints={validation_results['checkpoint_completed']}/{validation_results['checkpoint_total']}"
        )

        if validation_results["final_validation_status"] == "BROKEN":

            logger.critical(f"[TEST] Emergency Triggered: Reason={validation_results.get('final_validation_reason')}")
            self._handle_critical_validation_failure(validation_results)


    def _handle_critical_validation_failure(self, results: dict):
        logger.critical(
            f"[VALIDATION_FAILED] Cycle: {results.get('cycle_id')} | "
            f"Reason: {results.get('final_validation_reason')}"
        )
        self.runtime.write("health", "critical")
        self.runtime.write("worker_status", "stalled")
        self.runtime.write("state", "error")


    def _finalize_cycle(self, v_state):
        cycle_id = self.runtime.read("cycle_id")

        validation = dict(self.runtime.read("runtime_validation"))
        validation["finalize_checkpoint_seen"] = True
        self.runtime.write("runtime_validation", validation)

        run_automation(v_state)
        mark_checkpoint(v_state, "finalize_checkpoint_seen")

        if self.runtime.read("cycle_finalized"):
            return

        self.runtime.write("cycle_state", "CLOSING")
        self.runtime.write("cycle_end_ts", time.time())
        self.runtime.write("cycle_state", "CLOSED")
        self.runtime.write("cycle_finalized", True)

        self.runtime.emit_event("cycle_finalized", {"cycle_id": cycle_id})


    def start(self):
        if self.runtime.read("started"):
            return

        try:
            self.runtime.write("state", "starting")
            self.runtime.write("started", True)
            self.runtime.write("worker_status", "idle")
        except RuntimeError:

            logger.warning("[WORKER] Startup write restricted by Backbone Policy")

        logger.info("[WORKER] started")

        try:
            target = self.runtime.read("worker_target_count")
        except (AttributeError, RuntimeError):
            target = 1
        
        if target is None: 
            target = 1

        for _ in range(target):
            self.start_worker_thread()

    def start_worker_thread(self):
        t = threading.Thread(target=self.worker_loop, daemon=True)
        t.start()
        
        # Das hier funktioniert jetzt ohne Crash, auch wenn worker_threads neu ist:
        worker_threads = list(self.runtime.read("worker_threads") or [])
        worker_threads.append(t)

        logger.info(f"[TEST] Scaling Check: Target={self.runtime.read('worker_target_count')} Threads={len(worker_threads)}")
        
        try:
            self.runtime.write("worker_threads", worker_threads)
            self.runtime.write("worker_status", "idle")
        except RuntimeError:
            logger.warning("[WORKER] worker_threads write blocked by Backbone")

    def scale_workers(self):
        worker_target_count = self.runtime.read("worker_target_count")
        if worker_target_count >= MAX_WORKERS:
            logger.warning("[WORKER] max workers reached")
            return
        worker_target_count += 1
        self.runtime.write("worker_target_count", worker_target_count)
        self.runtime.write("worker_status", "processing")
        self.runtime.write("worker_last_activity", time.time())
        self.start_worker_thread()

    def scale_down(self):
        worker_target_count = self.runtime.read("worker_target_count")
        if worker_target_count <= 1:
            return
        worker_target_count -= 1
        self.runtime.write("worker_target_count", worker_target_count)
        self.runtime.write("worker_last_activity", time.time())
        worker_threads = list(self.runtime.read("worker_threads"))
        if worker_threads:
            worker_threads.pop()
            self.runtime.write("worker_threads", worker_threads)
            self.runtime.write("worker_status", "idle")

    def stop(self):
        self.runtime.write("started", False)
        self.runtime.write("worker_status", "idle")
        self.runtime.write("state", "stopped")
        self.runtime.write("current_request", None)
        self.runtime.write("busy", False)
        self.runtime.write("worker_threads", [])
        self.runtime.write("worker_target_count", 1)
        self.runtime.write("worker_last_activity", time.time())
