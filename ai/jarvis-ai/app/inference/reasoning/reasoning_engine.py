# VERIFY MARKER: UHqP+6J@

from inference.runtime_object import RUNTIME_ACCESS
from inference.runtime_automation import check_runtime_triggers
from inference.tools.tool_registry import list_tools

import time

class ReasoningEngine:


    def __init__(self):

        self.runtime = RUNTIME_ACCESS


    def observe(self):

        return {

            "state": self.runtime.read("state"),

            "health": self.runtime.read("health"),

            "queue": self.runtime.read("queue_size"),

            "busy": self.runtime.read("busy"),

            "metrics": self.runtime.read("metrics"),


        }


    def decide(self,observation):

        if observation["health"] == "error":

            return {

                "action":"alert",

                "reason":"runtime_error"

            }


        if observation["health"] == "degraded":

            return {

                "action":"monitor",

                "reason":"performance_degraded"

            }


        if observation["queue"] > 5:

            return {

                "action":"observe_queue",

                "reason":"queue_pressure"

            }


        return {

            "action":"none"

        }


    def execute(self,decision):

        return {

            "decision":decision

        }


    def cycle(self):
        observation = self.observe()
        decision = self.decide(observation)

        if decision.get("action") == "none":
            return None

        action = decision.get("action")

        # Deterministische Zuordnung
        if action == "alert":
            signal_type = "runtime_alert"
            severity = "high"
        elif action == "monitor":
            signal_type = "runtime_monitor"
            severity = "medium"
        elif action == "observe_queue":
            signal_type = "queue_pressure"
            severity = "low"
        else:
            signal_type = "unknown"
            severity = "low"

        state = observation.get("state")
        health = observation.get("health")
        busy = observation.get("busy")
        action = decision.get("action")

        # --- STATE BASED ELIGIBILITY ---

        # Regel 1: nur im aktiven Runtime-Zustand
        if state != "processing":
            return None

        # Regel 2: nur wenn System aktiv arbeitet
        if not busy:
            return None

        # Regel 3: Health-Validierung pro Action
        if action == "alert" and health != "error":
            return None

        if action == "monitor" and health != "degraded":
            return None

        # --- HISTORY BASED CONTROL ---

        signal_history = self.runtime.read("signal_history")

        last_same_signal_time = None

        # Suche letztes gleiches Signal
        for entry in reversed(signal_history):
            signals = entry.get("signals", [])

            for sig in signals:
                if (
                    sig.get("type") == signal_type and
                    sig.get("source") == "reasoning_engine"
                ):
                    last_same_signal_time = entry.get("time")
                    break

            if last_same_signal_time:
                break

        # Zeitregel (Cooldown)
        COOLDOWN_SECONDS = 10

        if last_same_signal_time:
            if time.time() - last_same_signal_time < COOLDOWN_SECONDS:
                return None

        candidate = {
            "type": signal_type,
            "source": "reasoning_engine",
            "severity": severity,
            "payload": {
                "decision": decision,
                "observation": observation
            },
            "metadata": {
                "generated_at": time.time()
            }
        }
        return candidate
