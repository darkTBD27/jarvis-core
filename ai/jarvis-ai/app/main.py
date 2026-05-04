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
from decision_engine.action_executor import set_runtime_worker

import logging
import os
from datetime import datetime


# -------------------------
# LOGGER SETUP
# -------------------------
logger = logging.getLogger("jarvis")

if not logger.handlers:
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"logs/jarvis_{timestamp}.log"

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


# -------------------------
# DEBUG: REAL FILE CHECK
# -------------------------
import inference.runtime_worker as rw
logger.warning(f"[DEBUG] RUNTIME WORKER FILE: {rw.__file__}")


# -------------------------
# APP SETUP
# -------------------------
BASE = Path(__file__).resolve().parent

app = FastAPI()
router = CommandRouter()


# -------------------------
# STARTUP
# -------------------------
@app.on_event("startup")
def startup_event():
    load_model("llama3")
    logger.info("Model loaded")

    runtime_worker = RuntimeWorker()

    set_runtime_worker(runtime_worker)

    runtime_worker.start()

    logger.info("[SYSTEM] Worker initialized and started")


# -------------------------
# ROUTES
# -------------------------
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
    return {"gpu": "available" if gpu_available() else "not available"}


@app.get("/models")
def models():
    return list_models()


@app.post("/inference")
def infer(prompt: str):
    return router.handle("infer", prompt)


@app.post("/cancel")
def cancel(request_id: str):
    return router.handle("cancel", {"request_id": request_id})


@app.post("/retry")
def retry(request_id: str):
    return router.handle("retry", {"request_id": request_id})


@app.post("/command")
def command(command: str, data: Any = Body(default=None)):
    return router.handle(command, data)


@app.get("/status")
def status():
    raw = get_status()

    engine = raw.get("inference", {}).get("engine", {})

    # fallback falls doppelt verschachtelt
    if "inference" in engine:
        engine = engine.get("inference", {}).get("engine", engine)

    return {
        "service": "jarvis-ai",
        "gpu": gpu_available(),
        "model": model_status(),
        "inference": {
            "engine": engine
        },
        "ready": True,
        "models": list_models()
    }


@app.get("/request")
def request(request_id: str):
    return router.handle("request", {"request_id": request_id})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    with open(BASE / "dashboard/status.html") as f:
        return f.read()
