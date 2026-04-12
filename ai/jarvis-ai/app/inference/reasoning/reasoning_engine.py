from inference.runtime_object import get_runtime
from inference.runtime_automation import check_runtime_triggers
from inference.tools.tool_registry import list_tools


class ReasoningEngine:


    def __init__(self):

        self.runtime = get_runtime()


    def observe(self):

        return {

            "state":self.runtime.state,

            "health":self.runtime.health,

            "queue":self.runtime.queue_size,

            "busy":self.runtime.busy,

            "tools":list_tools(),

            "metrics":self.runtime.metrics,

            "triggers":check_runtime_triggers()

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

        return self.execute(decision)
