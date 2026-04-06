from orchestrator.memory_commands import MemoryCommands
from inference.tools.tool_registry import get_tool

import services.runtime_service as runtime
import uuid
import time


SLOW_THRESHOLD = 10


def build_command_error(message):

    return {

        "error": True,
        "error_code": "UNKNOWN_COMMAND",
        "message": message

    }


class CommandRouter:


    def __init__(self):

        self.memory = MemoryCommands()

        # Telemetry
        self.command_history = []
        self.slow_history = []
        self.request_timestamps = []

        self.current_command = None

        # Counters
        self.total_commands = 0
        self.success_commands = 0
        self.error_commands = 0
        self.slow_commands = 0

        self.total_duration = 0.0

        # Command Registry
        self.commands = {

            "infer": {
                "handler": self.infer,
                "description": "führt Modell Inference aus"
            },

            "memory_set": {
                "handler": self.memory.set,
                "description": "speichert memory wert"
            },

            "memory_get": {
                "handler": self.memory.get,
                "description": "holt memory wert"
            },

            "memory_delete": {
                "handler": self.memory.delete,
                "description": "löscht memory wert"
            },

            "memory_list": {
                "handler": self.memory.list,
                "description": "zeigt memory"
            },

            "status": {
                "handler": self.status,
                "description": "zeigt AI Runtime Status"
            },

            "commands": {
                "handler": self.commands_list,
                "description": "listet verfügbare Befehle"
            },

            "history": {
                "handler": self.history,
                "description": "zeigt letzte commands"
            },

            "current": {
                "handler": self.current,
                "description": "zeigt aktuellen command"
            },

            "health": {
                "handler": self.health,
                "description": "zeigt system health"
            },

            "slow": {
                "handler": self.slow,
                "description": "zeigt langsame requests"
            },

            "request": {
                "handler": self.request,
                "description": "zeigt status einer request id"
            },

            "retry": {
                "handler": self.retry,
                "description": "retry einer request id"
            },

            "cancel": {
                "handler": self.cancel,
                "description": "cancel request"
            }

        }


    # ========================
    # COMMAND HANDLER
    # ========================

    def handle(self, command, data=None):

        request_id = str(uuid.uuid4())

        start_time = time.time()

        print(f"[COMMAND START] {command} request={request_id}")

        self.total_commands += 1

        self.request_timestamps.append(time.time())

        now = time.time()

        self.request_timestamps = [

            t for t in self.request_timestamps

            if now - t < 60

        ]

        self.current_command = {

            "request_id": request_id,
            "command": command,
            "start_time": start_time

        }

        # Unknown command
        if command not in self.commands:

            tool = get_tool(command)

            if tool:

                result = tool.execute(data)

                if not isinstance(result,dict):

                    result = {

                        "error":False,

                        "data":result

                    }

                return {

                    "request_id": request_id,
                    "command": command,
                    "duration": 0,
                    "result": result

                }

            print(f"[COMMAND ERROR] unknown command request={request_id}")

            self.error_commands += 1

            self.current_command = None

            return build_command_error("unknown command")

        # Execute command
        result = self.commands[command]["handler"](data, request_id)

        duration = round(time.time() - start_time, 3)

        self.total_duration += duration

        # Slow detection
        if duration > SLOW_THRESHOLD:

            self.slow_commands += 1

            self.slow_history.append({

                "request_id": request_id,
                "command": command,
                "duration": duration,
                "timestamp": round(time.time(), 2)

            })

        if len(self.slow_history) > 50:

            self.slow_history.pop(0)

        # Extract metrics
        tokens = None
        tokens_per_sec = None
        error = False

        if isinstance(result, dict):

            if "result" in result:

                inner = result["result"]

                tokens = inner.get("tokens")

                tokens_per_sec = inner.get("tokens_per_sec")

                error = inner.get("error", False)

        # Error / success counters
        if error:

            self.error_commands += 1

        else:

            self.success_commands += 1

        # History
        self.command_history.append({

            "request_id": request_id,
            "command": command,
            "timestamp": round(time.time(), 2),
            "duration": duration,
            "tokens": tokens,
            "tokens_per_sec": tokens_per_sec,
            "error": error

        })

        if len(self.command_history) > 100:

            self.command_history.pop(0)

        print(f"[COMMAND END] {command} request={request_id} time={duration}s")

        self.current_command = None

        return {

            "request_id": request_id,
            "command": command,
            "duration": duration,
            "result": result

        }


    # ========================
    # COMMAND FUNCTIONS
    # ========================

    def infer(self, data, request_id=None):

        if not data:

            return {

                "error": True,

                "message": "missing prompt"

            }

        cmd = str(data).lower().strip()

        if cmd == "status":

            return runtime.status()

        if cmd == "health":

            return self.health()

        if cmd == "commands":

            return self.commands_list()

        return runtime.run(data, request_id)


    def cancel(self, data=None, request_id=None):

        rid = None

        if data:

            rid = data.get("request_id")

        if not rid:

            return {

                "error": True,
                "message": "missing request_id"

            }

        return runtime.cancel(rid)


    def retry(self, data=None, request_id=None):

        rid = None

        if data:

            rid = data.get("request_id")

        if not rid:

            return {

                "error": True,
                "message": "missing request_id"

            }

        return runtime.retry(rid)


    def status(self, data=None, request_id=None):

        return runtime.status()


    def history(self, data=None, request_id=None):

        return {

            "history": self.command_history

        }


    def slow(self, data=None, request_id=None):

        return {

            "slow_requests": self.slow_history

        }


    def current(self, data=None, request_id=None):

        return {

            "current": self.current_command

        }


    def health(self, data=None, request_id=None):

        success_rate = 0
        avg_duration = 0

        requests_per_min = len(self.request_timestamps)

        if self.total_commands > 0:

            success_rate = round(

                (self.success_commands / self.total_commands) * 100,
                2

            )

            avg_duration = round(

                self.total_duration / self.total_commands,
                3

            )

        return {

            "total": self.total_commands,
            "success": self.success_commands,
            "errors": self.error_commands,
            "slow": self.slow_commands,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "requests_per_min": requests_per_min

        }


    def commands_list(self, data=None, request_id=None):

        return {

            "commands": {

                name: info["description"]

                for name, info in self.commands.items()

            }

        }


    def request(self, data=None, request_id=None):

        rid = None

        if data:

            rid = data.get("request_id")

        if not rid:

            return {

                "error": True,
                "message": "missing request_id"

            }

        return runtime.request(rid)
