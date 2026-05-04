from engine.logger import logger

import time
import copy
import threading
import traceback

ACCESS_TYPE_READ = "read"
ACCESS_TYPE_WRITE = "write"
ACCESS_TYPE_EVENT = "event"
ACCESS_TYPE_SYSTEM = "system"


class RuntimeState:

    def __setattr__(self, name, value):
        if not hasattr(self, "__initialized__"):
            object.__setattr__(self, name, value)
            return

        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return

        if getattr(self, "_write_allowed", False):
            context = getattr(self, "_write_context", None)
            if context is None:
                raise RuntimeError(f"[RUNTIME VIOLATION] Write without context detected for '{name}'")
            object.__setattr__(self, name, value)
            return

        protected_fields = {
            "state",
            "busy",
            "current_request",
            "started",
            "health",
            "queue_size",
            "worker_threads",
            "worker_target_count",
            "worker_status",
            "worker_heartbeat",
            "worker_last_activity",
            "inference_start",
            "last_request",
            "last_error",
            "last_error_at",
            "error_types",
            "error_history",
            "metrics",
            "history",
            "outcomes",
            "signal_history",
            "health_history",
            "last_decision",
            "decision_history",
            "request_status",
            "cancelled_requests",
            "runtime_events",
            "event_listeners",
            "request_timestamps",
            "queue_snapshot",
            "worker_error_count",
            "worker_last_error_time",
            "action_last_execution",
            "runtime_context",
            "runtime_validation",
            "cycle_id",
            "cycle_state",
            "cycle_start_ts",
            "cycle_end_ts",
            "cycle_finalized",
            "cycle_persist_failed",
            "snapshot_ts",
            "snapshot_committed",
            "snapshots",
            "last_snapshot_cycle_id",
        }

        if name in protected_fields:
            raise RuntimeError(
                f"[STATE OWNERSHIP VIOLATION] '{name}' is protected. "
                f"Mutation only allowed via RUNTIME_ACCESS.write()."
            )

        raise RuntimeError(
            f"[RUNTIME VIOLATION] Direct write to '{name}' is not allowed. "
            f"WriteContext={getattr(self, '_write_context', None)}"
        )


    def __getattribute__(self, name):
        allowed_internals = [
            "__dict__",
            "__class__",
            "__setattr__",
            "__getattribute__",
            "_runtime",
            "_write_allowed",
            "_write_context",
            "__initialized__"
        ]
        
        if name in allowed_internals:
            return object.__getattribute__(self, name)

        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None

    def __init__(self):
        self.inference_start = None
        self.state = "idle" 
        self.busy = False
        self.current_request = None
        self.started = False 
        self.start_time = time.time()

        self.worker_threads = []
        self.worker_target_count = 1
        self.worker_status = "starting"
        self.worker_heartbeat = time.time()
        self.worker_last_activity = time.time()

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
        self.outcomes = []
        self.MAX_OUTCOME_HISTORY = 200

        self.MAX_HISTORY = 100
        self.MAX_ERROR_HISTORY = 100
        self.signal_history = []
        self.MAX_SIGNAL_HISTORY = 100

        self.last_request = None
        self.last_error = None
        self.last_error_at = None
        self.error_types = {}
        self.error_history = []

        self.health_history = []
        self.MAX_HEALTH_HISTORY = 50

        self.last_decision = {}
        self.decision_history = []
        self.MAX_DECISION_HISTORY = 50

        self.request_status = {}
        self.cancelled_requests = set()
        self.runtime_events = []
        self.event_listeners = {}
        self.request_timestamps = []

        self._write_context = None
        self.queue_snapshot = []

        self.worker_error_count = 0
        self.worker_last_error_time = None
        self.action_last_execution = {}

        self.runtime_context = {}
        self.runtime_validation = {}

        self.cycle_id = None
        self.cycle_state = "IDLE"
        self.cycle_start_ts = None
        self.cycle_end_ts = None
        self.cycle_finalized = False
        self.cycle_persist_failed = False

        self.snapshot_ts = None
        self.snapshot_committed = False
        self.snapshots = []
        self.last_snapshot_cycle_id = None

        self.__initialized__ = True

    def set_state(self, state):
        raise RuntimeError("[RUNTIME VIOLATION] Direct state change not allowed. Use RUNTIME_ACCESS.write().")


    def set_busy(self, value):
        raise RuntimeError("[RUNTIME VIOLATION] Direct write not allowed. Use RUNTIME_ACCESS.write().")


    def set_health(self, state):
        raise RuntimeError("[RUNTIME VIOLATION] Direct write not allowed. Use RUNTIME_ACCESS.write().")


    def get_health(self):

        return self.health


    def clear_current(self):
        raise RuntimeError("[RUNTIME VIOLATION] Direct write not allowed. Use RUNTIME_ACCESS.write().")


    def set_current(self, request_id):
        raise RuntimeError("[RUNTIME VIOLATION] Direct write not allowed. Use RUNTIME_ACCESS.write().")


    def metric_inc(self,name):
        raise RuntimeError("[RUNTIME VIOLATION] Direct metric mutation not allowed. Use RUNTIME_ACCESS.metric_inc().")


    def metric_set(self, name, value):
        raise RuntimeError("[RUNTIME VIOLATION] Direct metric mutation not allowed. Use RUNTIME_ACCESS.metric_set().")


    def metric_get(self,name):

        return self.metrics.get(name,0)


    def add_history(self, entry):
        raise RuntimeError("[RUNTIME VIOLATION] Direct history mutation not allowed. Use RUNTIME_ACCESS.add_history().")


    def add_event(self, event_type, data=None):
        raise RuntimeError("[RUNTIME VIOLATION] Direct event mutation not allowed. Use RUNTIME_ACCESS.emit_event().")


    def get_worker_status(self):

        now = time.time()

        if now - self.worker_heartbeat > 10:

            return "stalled"

        if self.busy:

            return "processing"

        return "idle"


    def get_worker_heartbeat_age(self):

        snapshot_ts = self.snapshot_ts or time.time()
        return snapshot_ts - self.worker_heartbeat


    def get_worker_last_activity_age(self):

        snapshot_ts = self.snapshot_ts or time.time()
        return snapshot_ts - self.worker_last_activity


    def get_uptime(self):

        snapshot_ts = self.snapshot_ts or time.time()
        return int(snapshot_ts - self.start_time)


    def check_worker_health(self):

        now = time.time()

        if now - self.worker_heartbeat > 10:

            return "stalled"

        return "ok"


    def get_last_error(self):
        raise RuntimeError("[RUNTIME VIOLATION] External error access detected. Must be part of Runtime state.")


    def get_error_types(self):
        raise RuntimeError("[RUNTIME VIOLATION] External error access detected. Must be part of Runtime state.")


    def get_error_history(self):
        raise RuntimeError("[RUNTIME VIOLATION] External error access detected. Must be part of Runtime state.")


    def get_runtime_events(self):

        return list(self.runtime_events)


    def add_health_history(self, state):
        raise RuntimeError("[RUNTIME VIOLATION] Direct health mutation not allowed. Use RUNTIME_ACCESS.write().")


    def get_health_history(self):

        return self.health_history


    def add_signal_history(self, signals):
        raise RuntimeError("[RUNTIME VIOLATION] Direct signal mutation not allowed. Use RUNTIME_ACCESS.add_signal().")


    def add_outcome(self, outcome):
        raise RuntimeError("[RUNTIME VIOLATION] Direct outcome mutation not allowed. Use RUNTIME_ACCESS.write().")


class RuntimeAccess:

    ALLOWED_WRITE_KEYS = {

        "state",
        "busy",
        "current_request",
        "started",
        "start_time",
        "health",
        "error_types",

        "queue_size",
        "worker_heartbeat",
        "worker_last_activity",
        "worker_status",
        "worker_target_count",
        "worker_threads",
        "inference_start",

        "last_request",
        "last_error",
        "last_error_at",
        "error_history",

        "outcomes",
        "history",
        "signal_history",
        "health_history",
        "last_decision",
        "decision_history",

        "metrics",

        "request_status",
        "cancelled_requests",
        "runtime_events",
        "event_listeners",
        "request_timestamps",

        "queue_snapshot",
        "worker_error_count",
        "worker_last_error_time",
        "action_last_execution",
        "runtime_context",
        "cycle_id",
        "cycle_state",
        "cycle_start_ts",
        "cycle_end_ts",
        "cycle_finalized",
        "cycle_persist_failed",
        "snapshot_ts",
        "snapshot_committed",
        "snapshots",
        "last_snapshot_cycle_id",
        "runtime_validation"
    }

    ALLOWED_STATE_TRANSITIONS = {
        "idle": {
            "processing",
            "starting",
            "running",
            "stopped"
        },

        "starting": {
            "idle",
            "processing",
            "running",
            "stopped"
        },

        "processing": {
            "idle",
            "error",
            "running",
            "stopped"
        },

        "running": {
            "idle",
            "error",
            "processing",
            "stopped"
        },

        "error": {
            "idle",
            "stopped"
        },

        "stopped": {
            "starting",
            "idle"
        }
    }


    def __init__(self, runtime):

        if getattr(self.__class__, "_instance_created", False):
            return

        self._runtime = runtime
        self._write_lock = threading.Lock()

        self.__class__._instance_created = True
        runtime._access_initialized = True
        
        logger.warning(f"### BACKBONE SOURCE OF TRUTH INITIALIZED (ID: {id(self)}) ###")


    def _log(self, access_type, key=None, value=None, success=True, error=None):
        try:
            try:
                request_id = self._runtime.current_request
            except Exception:
                request_id = None

            msg = (
                f"[RUNTIME ACCESS] "
                f"type={access_type} "
                f"key={key} "
                f"value={value if access_type == ACCESS_TYPE_WRITE else None} "
                f"success={success} "
                f"request_id={request_id}"
            )

            if error:
                msg += f" error={type(error).__name__}"

            NOISY_KEYS = {
                "worker_heartbeat",
                "queue_size",
                "queue_snapshot",
                "worker_status",
                "signal_history",
                "state",
                "health",
                "busy",
                "metrics",
                "cycle_state",
                "runtime_validation"
            }

            if key in NOISY_KEYS:
                return

            if not success or error:
                logger.info(msg)
            else:
                logger.debug(msg)

        except Exception:
            pass


    def _classify(self, access_type):
        if access_type not in (
            ACCESS_TYPE_READ,
            ACCESS_TYPE_WRITE,
            ACCESS_TYPE_EVENT,
            ACCESS_TYPE_SYSTEM
        ):
            raise RuntimeError(f"[RUNTIME ACCESS VIOLATION] Invalid access type: {access_type}")


    def _validate_write(self, key, value, current_state=None):
        if key not in self.ALLOWED_WRITE_KEYS:
            raise RuntimeError(f"[RUNTIME VALIDATION] Write not allowed for key: {key}")

        if key in ("state", "worker_status") and value is None:
            raise RuntimeError(f"[RUNTIME VALIDATION] {key} cannot be None")

        if key == "busy" and not isinstance(value, bool):
            raise RuntimeError(f"[RUNTIME VALIDATION] busy must be bool")

        if key == "worker_threads" and not isinstance(value, list):
            raise RuntimeError(f"[RUNTIME VALIDATION] worker_threads must be list")

        EXPECTED_TYPES = {
            "state": str,
            "worker_status": str,
            "health": str,
            "busy": bool,
            "started": bool,
            "queue_size": int,
            "current_request": (str, type(None)),
            "last_request": (str, type(None)),
            "last_error": (str, type(None)),
            "error_history": list,
            "last_error_at": (float, type(None)),
            "error_types": dict,
            "worker_heartbeat": float,
            "worker_last_activity": float,
            "worker_target_count": int,
            "worker_threads": list,
            "inference_start": (float, type(None)),
            "outcomes": list,
            "history": list,
            "signal_history": list,
            "health_history": list,
            "last_decision": dict,
            "decision_history": list,
            "metrics": dict,
            "request_status": dict,
            "cancelled_requests": set,
            "runtime_events": list,
            "event_listeners": dict,
            "request_timestamps": list,
            "cycle_persist_failed": bool,
            "snapshot_committed": bool,
            "runtime_context": dict,
            "runtime_validation": dict
        }

        expected = EXPECTED_TYPES.get(key)

        if expected and value is not None and not isinstance(value, expected):
            raise RuntimeError(
                f"[RUNTIME VALIDATION] Invalid type for key '{key}': "
                f"expected {expected}, got {type(value)}"
            )

        if key == "state" and current_state in self.ALLOWED_STATE_TRANSITIONS:
            allowed_next = self.ALLOWED_STATE_TRANSITIONS[current_state]
            if value not in allowed_next:
                raise RuntimeError(
                    f"[RUNTIME VALIDATION] Invalid state transition: "
                    f"{current_state} → {value}"
                )

        if key == "queue_size" and not isinstance(value, int):
            raise RuntimeError("[RUNTIME VALIDATION] queue_size must be int")

        if key == "worker_threads":
            if not isinstance(value, list):
                raise RuntimeError(f"[RUNTIME VALIDATION] worker_threads must be list")
            
            for i, thread in enumerate(value):
                if not isinstance(thread, threading.Thread):
                    raise RuntimeError(f"[RUNTIME VALIDATION] worker_threads index {i} is invalid: {type(thread)}")
            
            target = self.read("worker_target_count")
            if len(value) > target:
                raise RuntimeError(f"[RUNTIME VALIDATION] Thread count {len(value)} exceeds target {target}")

        cycle_state = self.read("cycle_state")

        FINALIZE_KEYS = {
            "metrics",
            "history",
            "signal_history",
            "health_history",
            "snapshots",
            "last_snapshot_cycle_id",
            "snapshot_ts",
            "snapshot_committed",
            "cycle_persist_failed",
        }

        CYCLE_KEYS = {
            "cycle_id",
            "cycle_state",
            "cycle_start_ts",
            "cycle_end_ts",
            "cycle_finalized",
        }

        if key not in CYCLE_KEYS:
            if cycle_state == "CLOSING" and key not in FINALIZE_KEYS:
                raise RuntimeError(
                    f"[CYCLE VIOLATION] Write blocked during CLOSING: key={key}"
                )

            if cycle_state == "CLOSED" and key not in FINALIZE_KEYS:
                raise RuntimeError(
                    f"[CYCLE VIOLATION] Write blocked after CLOSED: key={key}"
                )


    def read(self, key):
        self._classify(ACCESS_TYPE_READ)

        try:

            result = object.__getattribute__(self._runtime, key)

            if isinstance(result, dict):
                result = dict(result)
            elif isinstance(result, list):
                result = list(result)
            elif isinstance(result, set):
                result = set(result)

            self._log(
                ACCESS_TYPE_READ,
                key=key,
                success=True
            )

            return result

        except Exception as e:
            self._log(
                ACCESS_TYPE_READ,
                key=key,
                success=False,
                error=e
            )
            raise


    def write(self, key, value):
        self._classify(ACCESS_TYPE_WRITE)

        try:
            current_state = None

            try:
                current_state = self.read("state")
            except Exception:
                pass

            self._validate_write(key, value, current_state=current_state)

            object.__setattr__(self._runtime, "_write_context", {
                "key": key,
                "time": time.time()
            })

            object.__setattr__(self._runtime, "_write_allowed", True)
            try:
                setattr(self._runtime, key, value)
            finally:
                object.__setattr__(self._runtime, "_write_allowed", False)
                object.__setattr__(self._runtime, "_write_context", None)

            self._log(
                ACCESS_TYPE_WRITE,
                key=key,
                value=value,
                success=True
            )

        except Exception as e:
            self._log(
                ACCESS_TYPE_WRITE,
                key=key,
                value=value,
                success=False,
                error=e
            )
            raise


    def emit_event(self, event_type, data=None):
        self._classify(ACCESS_TYPE_EVENT)

        try:

            events = list(self.read("runtime_events"))

            events.append({
                "type": event_type,
                "data": data,
                "time": time.time()
            })

            self._log(
                ACCESS_TYPE_EVENT,
                key="derived_write_runtime_events",
                value={"type": event_type},
                success=True
            )

            self._log(
                ACCESS_TYPE_EVENT,
                key="emit_event",
                value={"type": event_type},
                success=True
            )

            self.write("runtime_events", events)

            self._log(
                ACCESS_TYPE_EVENT,
                key=event_type,
                value=None,
                success=True
            )

        except Exception as e:
            self._log(
                ACCESS_TYPE_EVENT,
                key=event_type,
                success=False,
                error=e
            )
            raise


    def get_events(self):
        self._classify(ACCESS_TYPE_READ)

        try:

            value = list(self.read("runtime_events"))

            self._log(
                ACCESS_TYPE_READ,
                key="runtime_events",
                success=True
            )

            return value

        except Exception as e:
            self._log(
                ACCESS_TYPE_READ,
                key="runtime_events",
                success=False,
                error=e
            )
            raise


    def get_metric(self, name):
        self._classify(ACCESS_TYPE_SYSTEM)

        try:
            metrics = self.read("metrics")
            value = metrics.get(name, 0)

            self._log(
                ACCESS_TYPE_SYSTEM,
                key=name,
                value=value,
                success=True
            )

            return value

        except Exception as e:
            self._log(
                ACCESS_TYPE_SYSTEM,
                key=name,
                success=False,
                error=e
            )
            raise


    def add_history(self, entry):
        self._classify(ACCESS_TYPE_SYSTEM)

        try:

            history = list(self.read("history"))

            if len(history) >= self._runtime.MAX_HISTORY:
                history.pop(0)

            history.append(entry)

            self._log(
                ACCESS_TYPE_SYSTEM,
                key="derived_write_history",
                value={"size": len(history)},
                success=True
            )

            self.write("history", history)

            self._log(
                ACCESS_TYPE_SYSTEM,
                key="add_history",
                value={"entry": entry},
                success=True
            )

            self._log(
                ACCESS_TYPE_SYSTEM,
                key="history",
                value=None,
                success=True
            )

        except Exception as e:
            self._log(
                ACCESS_TYPE_SYSTEM,
                key="history",
                success=False,
                error=e
            )
            raise


    def metric_inc(self, name, value=1):
        self._classify(ACCESS_TYPE_SYSTEM)

        self._log(
            ACCESS_TYPE_SYSTEM,
            key="metric_inc",
            value={"name": name, "value": value},
            success=True
        )

        try:
            for _ in range(value):

                metrics = dict(self.read("metrics"))

                self._log(
                    ACCESS_TYPE_SYSTEM,
                    key="derived_write_metrics",
                    value={"name": name},
                    success=True
                )

                metrics[name] = metrics.get(name, 0) + 1

                self.write("metrics", metrics)

            self._log(
                ACCESS_TYPE_SYSTEM,
                key=name,
                value=value,
                success=True
            )

        except Exception as e:
            self._log(
                ACCESS_TYPE_SYSTEM,
                key=name,
                success=False,
                error=e
            )
            raise


    def metric_set(self, name, value):
        self._classify(ACCESS_TYPE_SYSTEM)

        self._log(
            ACCESS_TYPE_SYSTEM,
            key="metric_set",
            value={"name": name, "value": value},
            success=True
        )

        try:

            metrics = dict(self.read("metrics"))

            self._log(
                ACCESS_TYPE_SYSTEM,
                key="derived_write_metrics",
                value={"name": name},
                success=True
            )

            metrics[name] = value

            self.write("metrics", metrics)

            self._log(
                ACCESS_TYPE_SYSTEM,
                key=name,
                value=value,
                success=True
            )

        except Exception as e:
            self._log(
                ACCESS_TYPE_SYSTEM,
                key=name,
                success=False,
                error=e
            )
            raise


    def metric_get(self, name):
        self._classify(ACCESS_TYPE_SYSTEM)

        try:
            metrics = self.read("metrics")
            value = metrics.get(name, 0)

            self._log(
                ACCESS_TYPE_SYSTEM,
                key=name,
                value=value,
                success=True
            )

            return value

        except Exception as e:
            self._log(
                ACCESS_TYPE_SYSTEM,
                key=name,
                success=False,
                error=e
            )
            raise

    def build_snapshot(self):

        cycle_state = self.read("cycle_state")
        snapshot_ts = self.read("snapshot_ts")

        if cycle_state != "CLOSED":
            raise RuntimeError("[SNAPSHOT] Cannot build snapshot: cycle not CLOSED")

        if snapshot_ts is None:
            raise RuntimeError("[SNAPSHOT] snapshot_ts missing")

        snapshot = copy.deepcopy(self.SNAPSHOT_TEMPLATE)

        # timestamp
        snapshot["timestamp"] = snapshot_ts

        # runtime
        snapshot["runtime"] = {
            "state": self.read("state"),
            "busy": self.read("busy"),
            "health": self.read("health"),
            "current_request": self.read("current_request"),
            "last_request": self.read("last_request"),
        }

        # worker
        snapshot["worker"] = {

            "status": self.read("worker_status"),
            "worker_heartbeat": self.read("worker_heartbeat"),
            "worker_last_activity": self.read("worker_last_activity")
        }

        # queue
        snapshot["queue"] = {
            "size": self.read("queue_size")
        }

        metrics = self.read("metrics")
        snapshot["metrics"] = {
            k: metrics.get(k, 0)
            for k in snapshot["metrics"].keys()
        }

        # decision
        snapshot["decision"] = {
            "last": dict(self.read("last_decision") or {}),
            "recent": list(self.read("decision_history"))[-10:]
        }

        # errors
        snapshot["errors"] = {
            "last_error": self.read("last_error"),
            "error_types": dict(self.read("error_types") or {}),
            "error_history": list(self.read("error_history"))[-10:]
        }

        # history
        snapshot["history"] = {
            "recent": list(self.read("history"))[-10:],
            "outcomes": list(self.read("outcomes"))[-10:],
            "health": list(self.read("health_history"))[-10:]
        }

        # signals
        snapshot["signals"] = {
            "recent": list(self.read("signal_history"))[-10:]
        }

        return snapshot


    def commit_snapshot(self, snapshot):

        cycle_id = self.read("cycle_id")
        last_cycle = self.read("last_snapshot_cycle_id")

        if cycle_id == last_cycle:
            raise RuntimeError("[SNAPSHOT] Duplicate commit blocked")

        snapshots = list(self.read("snapshots"))
        snapshots.append(snapshot)

        self.write("snapshots", snapshots)
        self.write("last_snapshot_cycle_id", cycle_id)

        logger.info(f"[SNAPSHOT] committed cycle={cycle_id}")


    def add_health_history(self, state):
        self._classify(ACCESS_TYPE_SYSTEM)

        try:
            history = list(self.read("health_history"))

            if len(history) >= self._runtime.MAX_HEALTH_HISTORY:
                history.pop(0)

            history.append({
                "state": state,
                "time": time.time()
            })

            self.write("health_history", history)

        except Exception as e:
            self._log(
                ACCESS_TYPE_SYSTEM,
                key="health_history",
                success=False,
                error=e
            )
            raise


    def add_outcome(self, outcome):
        self._classify(ACCESS_TYPE_SYSTEM)

        try:
            outcomes = list(self.read("outcomes"))

            if len(outcomes) >= self._runtime.MAX_OUTCOME_HISTORY:
                outcomes.pop(0)

            outcomes.append(outcome)

            self.write("outcomes", outcomes)

        except Exception as e:
            self._log(
                ACCESS_TYPE_SYSTEM,
                key="outcomes",
                success=False,
                error=e
            )
            raise


    def add_signal(self, signals):
        self._classify(ACCESS_TYPE_EVENT)

        try:
            # --- STRUKTUR VALIDIERUNG (KEINE LOGIK) ---
            if not isinstance(signals, list):
                raise RuntimeError("[SIGNAL VALIDATION] signals must be list")

            for signal in signals:
                if not isinstance(signal, dict):
                    raise RuntimeError("[SIGNAL VALIDATION] signal must be dict")

                required_keys = [
                    "type",
                    "source",
                    "severity",
                    "payload",
                    "metadata"
                ]

                for key in required_keys:
                    if key not in signal:
                        raise RuntimeError(f"[SIGNAL VALIDATION] Missing key: {key}")

            # --- PERSIST ONLY ---
            current = list(self.read("signal_history"))

            updated = current + [{
                "signals": signals,
                "time": time.time()
            }]

            self._log(
                ACCESS_TYPE_EVENT,
                key="derived_write_signal_history",
                value={"count": len(updated)},
                success=True
            )

            self.write("signal_history", updated)

            self._log(
                ACCESS_TYPE_EVENT,
                key="add_signal",
                value={"signals": signals},
                success=True
            )

        except Exception as e:
            self._log(
                ACCESS_TYPE_EVENT,
                key="signal_history",
                value=signals,
                success=False,
                error=e
            )
            raise


    def validate_consistency(self):
        self._classify(ACCESS_TYPE_SYSTEM)

        try:
            snapshots = list(self.read("snapshots"))

            if snapshots:
                last_snapshot = snapshots[-1]
                runtime_state = self.read("state")
                snapshot_state = last_snapshot["runtime"]["state"]

                if runtime_state != snapshot_state:
                    raise RuntimeError(
                        f"[CONSISTENCY ERROR] State mismatch: runtime={runtime_state} snapshot={snapshot_state}"
                    )

            metrics = self.read("metrics")
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and value < 0:
                    raise RuntimeError(f"[CONSISTENCY ERROR] Negative metric: {key}={value}")

            history = self.read("history")
            if len(history) > self._runtime.MAX_HISTORY:
                raise RuntimeError("[CONSISTENCY ERROR] History overflow")

            signals = self.read("signal_history")
            if len(signals) > self._runtime.MAX_SIGNAL_HISTORY:
                raise RuntimeError("[CONSISTENCY ERROR] Signal history overflow")

            decisions = self.read("decision_history")
            if len(decisions) > self._runtime.MAX_DECISION_HISTORY:
                raise RuntimeError("[CONSISTENCY ERROR] Decision history overflow")

            now = time.time()
            start_time = self.read("start_time")

            state = self.read("state")
            busy = self.read("busy")
            health = self.read("health")
            started = self.read("started")

            worker_status = self.read("worker_status")
            worker_heartbeat = self.read("worker_heartbeat")
            worker_last_activity = self.read("worker_last_activity")
            worker_target_count = self.read("worker_target_count")
            worker_threads = self.read("worker_threads")

            current_request = self.read("current_request")
            inference_start = self.read("inference_start")

            cycle_state = self.read("cycle_state")
            cycle_finalized = self.read("cycle_finalized")
            cycle_persist_failed = self.read("cycle_persist_failed")
            cycle_start_ts = self.read("cycle_start_ts")
            cycle_end_ts = self.read("cycle_end_ts")

            snapshot_committed = self.read("snapshot_committed")
            snapshot_ts = self.read("snapshot_ts")

            last_decision = self.read("last_decision")
            last_error = self.read("last_error")
            last_error_at = self.read("last_error_at")
            error_types = self.read("error_types")
            error_history = self.read("error_history")
            decision_history = self.read("decision_history")

            if worker_status is None:
                raise RuntimeError("[CONSISTENCY ERROR] worker_status missing")

            if worker_heartbeat is None:
                raise RuntimeError("[CONSISTENCY ERROR] worker_heartbeat missing")

            if not isinstance(worker_threads, list):
                raise RuntimeError("[CONSISTENCY ERROR] worker_threads invalid")

            if len(worker_threads) > worker_target_count:
                raise RuntimeError("[CONSISTENCY ERROR] worker_threads exceed target")

            if worker_target_count < 1:
                raise RuntimeError("[CONSISTENCY ERROR] worker_target_count invalid")

            if snapshot_committed and snapshot_ts is None:
                raise RuntimeError("[CONSISTENCY ERROR] snapshot committed without timestamp")

            if snapshot_committed and cycle_state != "CLOSED":
                raise RuntimeError("[CONSISTENCY ERROR] snapshot committed before cycle closed")

            if cycle_persist_failed and snapshot_committed:
                raise RuntimeError("[CONSISTENCY ERROR] snapshot committed after persist failure")

            if cycle_finalized and cycle_end_ts is None:
                raise RuntimeError("[CONSISTENCY ERROR] finalized cycle missing end timestamp")

            if cycle_state == "CLOSED" and not cycle_finalized:
                raise RuntimeError("[CONSISTENCY ERROR] closed cycle not finalized")

            if cycle_state == "ERROR" and health not in {"degraded", "critical"}:
                raise RuntimeError("[CONSISTENCY ERROR] error cycle without degraded health")

            if cycle_state == "CLOSED" and cycle_start_ts is None:
                raise RuntimeError("[CONSISTENCY ERROR] closed cycle without start timestamp")

            if cycle_state == "CLOSED" and cycle_end_ts is None:
                raise RuntimeError("[CONSISTENCY ERROR] closed cycle without end timestamp")

            if cycle_state == "CLOSED" and snapshot_ts is None and not cycle_persist_failed:
                raise RuntimeError("[CONSISTENCY ERROR] closed cycle without snapshot")

            if busy and current_request is None:
                raise RuntimeError("[CONSISTENCY ERROR] busy without current_request")

            if busy and inference_start is None:
                raise RuntimeError("[CONSISTENCY ERROR] busy without inference_start")

            if not busy and inference_start is not None:
                raise RuntimeError("[CONSISTENCY ERROR] inference_start without busy")

            if inference_start is not None and current_request is None:
                raise RuntimeError("[CONSISTENCY ERROR] inference_start without current_request")

            if worker_status == "processing" and not busy:
                raise RuntimeError("[CONSISTENCY ERROR] worker processing while runtime not busy")

            if worker_status == "processing" and current_request is None:
                raise RuntimeError("[CONSISTENCY ERROR] processing worker without request")

            if worker_status == "idle" and busy:
                raise RuntimeError("[CONSISTENCY ERROR] idle worker while runtime busy")

            if worker_status == "idle" and state == "processing" and not current_request:
                raise RuntimeError("[CONSISTENCY ERROR] processing state without active request")

            if worker_status == "stalled" and health not in {"degraded", "critical"}:
                raise RuntimeError("[CONSISTENCY ERROR] stalled worker without degraded health")

            if state == "idle" and busy:
                raise RuntimeError("[CONSISTENCY ERROR] idle state while busy")

            if state == "idle" and current_request is not None:
                raise RuntimeError("[CONSISTENCY ERROR] idle state with active current_request")

            if state == "idle" and inference_start is not None:
                raise RuntimeError("[CONSISTENCY ERROR] idle state with active inference_start")

            if state == "processing" and worker_status == "stalled":
                raise RuntimeError("[CONSISTENCY ERROR] processing state with stalled worker")

            if state == "error" and worker_status not in {"stalled", "idle"}:
                raise RuntimeError("[CONSISTENCY ERROR] error state with invalid worker status")

            if state == "stopped" and started:
                raise RuntimeError("[CONSISTENCY ERROR] stopped state while started")

            if state == "stopped" and worker_threads:
                raise RuntimeError("[CONSISTENCY ERROR] stopped state with active worker threads")

            if last_decision and not isinstance(last_decision, dict):
                raise RuntimeError("[CONSISTENCY ERROR] last_decision invalid")

            if last_error and not error_types:
                raise RuntimeError("[CONSISTENCY ERROR] last_error without error_types")

            if last_error and last_error_at is None:
                raise RuntimeError("[CONSISTENCY ERROR] last_error missing timestamp")

            if last_error_at is not None and not last_error:
                raise RuntimeError("[CONSISTENCY ERROR] error timestamp without last_error")

            if last_error_at is not None and last_error_at > now:
                raise RuntimeError("[CONSISTENCY ERROR] last_error_at in future")

            if last_error_at is not None and last_error_at < start_time:
                raise RuntimeError("[CONSISTENCY ERROR] last_error_at before runtime start")

            if not isinstance(decision_history, list):
                raise RuntimeError("[CONSISTENCY ERROR] decision_history invalid")

            if len(decision_history) > self._runtime.MAX_DECISION_HISTORY:
                raise RuntimeError("[CONSISTENCY ERROR] decision_history overflow")

            if not isinstance(error_history, list):
                raise RuntimeError("[CONSISTENCY ERROR] error_history invalid")

            if len(error_history) > self._runtime.MAX_ERROR_HISTORY:
                raise RuntimeError("[CONSISTENCY ERROR] error_history overflow")

            if inference_start is not None and inference_start > now:
                raise RuntimeError("[CONSISTENCY ERROR] inference_start in future")

            if inference_start is not None and inference_start < start_time:
                raise RuntimeError("[CONSISTENCY ERROR] inference_start before runtime start")

            if worker_last_activity < start_time:
                raise RuntimeError("[CONSISTENCY ERROR] worker_last_activity before runtime start")

            if worker_last_activity > now:
                raise RuntimeError("[CONSISTENCY ERROR] worker_last_activity in future")

            if worker_heartbeat < start_time:
                raise RuntimeError("[CONSISTENCY ERROR] worker_heartbeat before runtime start")

            if worker_heartbeat > now:
                raise RuntimeError("[CONSISTENCY ERROR] worker_heartbeat in future")

            if snapshot_ts is not None and snapshot_ts < start_time:
                raise RuntimeError("[CONSISTENCY ERROR] snapshot_ts before runtime start")

            if snapshot_ts is not None and snapshot_ts > now:
                raise RuntimeError("[CONSISTENCY ERROR] snapshot_ts in future")

            if cycle_end_ts is not None and cycle_start_ts is not None and cycle_end_ts < cycle_start_ts:
                raise RuntimeError("[CONSISTENCY ERROR] cycle_end before cycle_start")

            if cycle_start_ts is not None and cycle_start_ts < start_time:
                raise RuntimeError("[CONSISTENCY ERROR] cycle_start before runtime start")

            if cycle_start_ts is not None and cycle_start_ts > now:
                raise RuntimeError("[CONSISTENCY ERROR] cycle_start in future")

            if cycle_end_ts is not None and cycle_end_ts > now:
                raise RuntimeError("[CONSISTENCY ERROR] cycle_end in future")

            if snapshot_ts is not None and cycle_end_ts is not None and snapshot_ts < cycle_end_ts:
                raise RuntimeError("[CONSISTENCY ERROR] snapshot before cycle end")

            self._log(
                ACCESS_TYPE_SYSTEM,
                key="consistency_check",
                value={"status": "ok"},
                success=True
            )

            return True

        except Exception as e:
            self._log(
                ACCESS_TYPE_SYSTEM,
                key="consistency_check",
                success=False,
                error=e
            )
            raise

    SNAPSHOT_SCHEMA_VERSION = 1

    SNAPSHOT_TEMPLATE = {

        "version": SNAPSHOT_SCHEMA_VERSION,

        "timestamp": 0,

        "runtime": {
            "state": None,
            "busy": None,
            "health": None,
            "current_request": None,
            "last_request": None
        },

        "worker": {
            "status": None,
            "worker_heartbeat": 0,
            "worker_last_activity": 0
        },

        "queue": {
            "size": 0
        },

        "metrics": {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "requests_timeout": 0,
            "queue_processed": 0,
            "priority_requests": 0,
            "slow_requests": 0,
            "avg_duration": 0,
            "last_duration": 0,
            "tokens_per_sec": 0
        },

        "decision": {
            "last": {},
            "recent": []
        },

        "errors": {
            "last_error": None,
            "last_error_at": None,
            "error_types": {},
            "error_history": []
        },

        "history": {
            "recent": [],
            "outcomes": [], 
            "health": []
        },

        "signals": {
            "recent": []
        }

    }


    def evaluate_candidate(self, candidate):
        self._classify(ACCESS_TYPE_SYSTEM)

        if candidate is None:
            return

        # --- BASIC VALIDATION ---
        required_keys = ["type", "source", "severity", "payload", "metadata"]

        for key in required_keys:
            if key not in candidate:
                return

        # --- FINAL DECISION: ACCEPT ---
        signal = {
            "type": candidate["type"],
            "source": candidate["source"],
            "severity": candidate["severity"],
            "payload": candidate["payload"],
            "metadata": candidate["metadata"]
        }

        # Übergang → echtes Signal
        self.add_signal([signal])


# interne Singleton-Instanz (nicht importieren, nur über RUNTIME_ACCESS benutzen)
_RUNTIME = RuntimeState()

# SINGLE ACCESS INSTANCE
RUNTIME_ACCESS = RuntimeAccess(_RUNTIME)

def get_runtime():
    raise RuntimeError("[RUNTIME VIOLATION] get_runtime() is not allowed. Use RUNTIME_ACCESS.")


def get_context(key):
    raise RuntimeError("[RUNTIME VIOLATION] get_context() removed. Use RUNTIME_ACCESS.read().")


def update_context(key, value):
    raise RuntimeError("[RUNTIME VIOLATION] update_context() removed. Use RUNTIME_ACCESS.write().")
