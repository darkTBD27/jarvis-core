from services.inference_request import InferenceRequest

from engine.engine_interface import run_engine
from engine.engine_interface import get_engine_status
from engine.engine_interface import get_request
from engine.engine_interface import cancel as engine_cancel
from engine.engine_interface import retry

from services.memory_service import MemoryService
from services.prompt_builder import build_prompt
from services.request_context import RequestContext
from services.conversation_store import ConversationStore

from core.intent_registry import get_intent
from core.intent_registry import get_system_command
from core.intent_registry import INTENT_SYSTEM
from core.intent_registry import INTENT_STATUS
from core.intent_registry import INTENT_MEMORY
from core.intent_registry import INTENT_HELP
from core.intent_registry import INTENT_CLEAR
from core.intent_registry import INTENT_TOOL

import time


REQUEST_TIMEOUT = 30


class InferenceService:


    def __init__(self):

        self.memory = MemoryService()
        self.conversations = ConversationStore()


    def build_request(self, prompt: str, request_id=None) -> InferenceRequest:

        if not prompt:
            raise ValueError("prompt empty")        
        
        intent = get_intent(prompt)

        conversation_id = request_id

        context = RequestContext(
            prompt=prompt,
            request_id=request_id,
            intent=intent,
            conversation_id=conversation_id
        )

        context.set_status("building_request")
        context.set_execution_path("unknown")


        # SYSTEM REQUESTS
        if intent == INTENT_SYSTEM:

            command = get_system_command(prompt)
        
            context.set_execution_path("system")
            context.add_meta("system_command", command)

            request = InferenceRequest(

                request_id=request_id,
                prompt=prompt.strip(),
                original_prompt=prompt.strip(),
                memory_context=None,
                memory_enabled=False

            )

            request.context = context

            return request


        # TOOL REQUESTS
        if intent == INTENT_TOOL:

            context.set_execution_path("tool")

            request = InferenceRequest(

                request_id=request_id,
                prompt=prompt.strip(),
                original_prompt=prompt.strip(),
                memory_context=None,
                memory_enabled=False

            )

            request.context = context

            return request


        # AI REQUESTS

        memory_enabled = True
        memory_context = self.memory.list()

        conversation_history = self.conversations.get_history(conversation_id)

        final_prompt = build_prompt(

            prompt,
            memory_context,
            memory_enabled,
            conversation_history

        )

        context.set_execution_path("ai")

        request = InferenceRequest(

            request_id=request_id,
            prompt=final_prompt,
            original_prompt=prompt.strip(),
            memory_context=memory_context,
            memory_enabled=memory_enabled

        )

        request.context = context

        return request


    def submit_request(self, request: InferenceRequest):

        # SYSTEM COMMAND FAST PATH
        if hasattr(request,"context") and request.context.execution_path == "system":

            command = request.context.metadata.get("system_command")

            if command == INTENT_STATUS:

                return {

                    "request_id":request.request_id,
                    "status":"finished",
                    "duration":0,
                    "error":False,
                    "route":"status",
                    "data":get_engine_status()

                }

            if command == INTENT_MEMORY:

                return {

                    "request_id":request.request_id,
                    "status":"finished",
                    "duration":0,
                    "error":False,
                    "route":"memory",
                    "data":self.memory.list()

                }

            if command == INTENT_HELP:

                return {

                    "request_id":request.request_id,
                    "status":"finished",
                    "duration":0,
                    "error":False,
                    "route":"help",
                    "commands":[

                        "status",
                        "memory",
                        "help",
                        "clear",
                        "tool:<name>"

                    ]

                }

            if command == INTENT_CLEAR:

                self.conversations.clear(
                    request.context.conversation_id
                )

                return {

                    "request_id":request.request_id,
                    "status":"finished",
                    "duration":0,
                    "error":False,
                    "route":"clear",
                    "message":"conversation cleared"

                }


        # TOOL FAST PATH
        if hasattr(request,"context") and request.context.execution_path == "tool":

            return run_engine(request)


        # AI EXECUTION PATH

        request.status = "running"
        
        if hasattr(request,"context"):
            request.context.set_status("running")

        try:

            if hasattr(request,"context"):

                self.conversations.add_message(

                    request.context.conversation_id,
                    "user",
                    request.original_prompt

                )

            result = run_engine(request)

            if hasattr(request,"context"):

                if isinstance(result,dict) and "response" in result:

                    self.conversations.add_message(

                        request.context.conversation_id,
                        "assistant",
                        result["response"]

                    )

            if isinstance(result, dict) and result.get("error"):

                request.status = "failed"
                
                if hasattr(request,"context"):
                    request.context.set_status("failed")

            else:

                request.status = "finished"
                
                if hasattr(request,"context"):
                    request.context.set_status("finished")

        except Exception as e:

            request.status = "crashed"
            
            if hasattr(request,"context"):
                request.context.set_status("crashed")

            result = {

                "error": True,
                "message": str(e)

            }

        finally:

            request.finished_at = time.time()

            request.duration = round(

                request.finished_at - request.created_at,
                3

            )

            if request.duration > REQUEST_TIMEOUT:

                request.status = "timeout"
                
                if hasattr(request,"context"):
                    request.context.set_status("timeout")


        return {

            "request_id": request.request_id,
            "status": request.status,
            "duration": request.duration,
            **result

        }


    def status(self):

        engine = get_engine_status()

        last = None

        if engine.get("history"):

            last_entry = engine["history"][-1]

            last = {

                "request_id": last_entry["request_id"],
                "status": last_entry["status"],
                "duration": last_entry["duration"]

            }


        return {

            "engine": engine,
            "last_request": last,
            "total_requests": engine["total_requests"],
            "success_requests": engine["success_requests"],
            "error_requests": engine["error_requests"],
            "slow_requests": engine["slow_requests"],
            "avg_duration": engine["avg_duration"],
            "history": engine["history"],
            "busy": engine["busy"],
            "current_request": engine["current_request"],
            "queue": engine["queue"]

        }


    def request(self, request_id):

        return get_request(request_id)


    def retry(self, request_id):

        return retry(request_id)


    def cancel(self, request_id):

        return engine_cancel(request_id)
