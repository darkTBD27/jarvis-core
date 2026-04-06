from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse

from gpu import gpu_available

from typing import Any

from models.models_service import list_models
from models.model_loader import load_model, model_status


from inference.runtime_worker import RuntimeWorker

from orchestrator.command_router import CommandRouter

from services.status_service import get_status
from pathlib import Path

import threading

BASE = Path(__file__).resolve().parent

app = FastAPI()

router = CommandRouter()

@app.on_event("startup")
def startup_event():
    load_model("llama3")

    print("Model loaded")

    runtime_worker = RuntimeWorker()

    worker_thread = threading.Thread(
        target=runtime_worker.start,
        daemon=True
    )

    worker_thread.start()

@app.get("/health")
def health():
    status = model_status()

    if not status["loaded"]:
        return {
            "service": "jarvis-ai",
            "status": "loading"
    }

    return {
        "service": "jarvis-ai",
        "status": "ready"
    }

@app.get("/gpu")
def gpu():

    if gpu_available():
        return {"gpu": "available"}

    return {"gpu": "not available"}

@app.get("/models")
def models():

    return list_models()

@app.post("/inference")
def infer(prompt: str):

    return router.handle("infer", prompt)

@app.post("/cancel")

def cancel(request_id: str):

    return router.handle(

        "cancel",

        {

            "request_id": request_id

        }

    )

@app.post("/retry")

def retry(request_id: str):

    return router.handle(

        "retry",

        {

            "request_id": request_id

        }

    )

@app.post("/command")
def command(command: str, data: Any = Body(default=None)):

    return router.handle(command, data)

@app.get("/status")
def status():

    return {
        "service":"jarvis-ai",
        
        "gpu":gpu_available(),
        
        "model":model_status(),

        "inference":{
            "engine":get_status()
        },
        
        "ready": True,

        "models":list_models()
    }

@app.get("/request")
def request(request_id: str):

    return router.handle(

        "request",

        {"request_id": request_id}

    )
    
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():

    with open(BASE / "dashboard/status.html") as f:
        return f.read()
