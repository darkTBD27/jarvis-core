from inference.tools.tool_base import JarvisTool

from inference.runtime_object import get_runtime


class SystemTool(JarvisTool):

    def __init__(self):

        super().__init__("system")


    def execute(self,data):

        runtime = get_runtime()

        return {

            "error": False,

            "data": {

                "state":runtime.state,

                "health":runtime.health,

                "queue":runtime.queue_size

            }

        }
