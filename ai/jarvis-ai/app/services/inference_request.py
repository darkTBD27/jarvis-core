from dataclasses import dataclass

import uuid
import time
import os


REQUEST_REGISTRY = {}

MAX_REQUEST_HISTORY = int(os.getenv("REQUEST_HISTORY_LIMIT","100"))


def cleanup_request_registry():

    if len(REQUEST_REGISTRY) > MAX_REQUEST_HISTORY:

        oldest = list(REQUEST_REGISTRY.keys())[0]

        del REQUEST_REGISTRY[oldest]


@dataclass
class InferenceRequest:

    request_id: str | None
    prompt: str

    original_prompt: str | None = None

    max_tokens: int = 150
    temperature: float = 0.3

    memory_context: dict | None = None
    memory_enabled: bool = False

    created_at: float = 0.0

    status: str = "created"
    finished_at: float | None = None
    duration: float | None = None


    def __post_init__(self):

        if not self.prompt:
            raise ValueError("prompt darf nicht leer sein")

        if not self.request_id:
            self.request_id = str(uuid.uuid4())

        if self.original_prompt is None:
            self.original_prompt = self.prompt

        if self.created_at == 0:
            self.created_at = time.time()

        REQUEST_REGISTRY[self.request_id] = self

        cleanup_request_registry()


    def set_status(self,status):

        self.status = status


    def mark_processing(self):

        self.status = "processing"


    def mark_finished(self):

        self.status = "finished"

        self.finished_at = time.time()

        self.duration = round(self.finished_at - self.created_at,2)


    def mark_error(self):

        self.status = "error"

        self.finished_at = time.time()

        self.duration = round(self.finished_at - self.created_at,2)


def get_request_status(request_id):

    req = REQUEST_REGISTRY.get(request_id)

    if not req:
        return None

    return {

        "request_id": req.request_id,

        "status": req.status,

        "created_at": req.created_at,

        "duration": req.duration

    }
