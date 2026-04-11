import time
from inference.queue_system import get_queue_size

current_worker_limit = 1
MAX_WORKERS = 3

last_scale_time = 0
SCALE_COOLDOWN = 5  # Sekunden

runtime_worker = None


def set_runtime_worker(worker):
    global runtime_worker
    runtime_worker = worker


def execute_action(action):

    global current_worker_limit
    global last_scale_time

    if not action:
        return

    print(f"[ACTION] Executing: {action}")

    if action == "scale_queue":

        now = time.time()

        # --- COOLDOWN ---
        if now - last_scale_time < SCALE_COOLDOWN:
            print("[SCALING] cooldown active")
            return

        queue = get_queue_size()

        print(f"[ACTION EXECUTOR] scale_queue | queue={queue}")

        if queue < 2:
            print("[SCALING] queue too small → skip")
            return

        if current_worker_limit < MAX_WORKERS:
            current_worker_limit += 1
            last_scale_time = now

            print(f"[SCALING] worker_limit increased to {current_worker_limit}")

            if runtime_worker:
                runtime_worker.scale_workers()
            else:
                print("[ERROR] runtime_worker not set")

        else:
            print("[SCALING] max workers reached")

    elif action == "scale_down":

        print("[ACTION EXECUTOR] scale_down triggered")

        if current_worker_limit > 1:
            current_worker_limit -= 1
            print(f"[SCALING] worker_limit decreased to {current_worker_limit}")

            if runtime_worker:
                runtime_worker.scale_down()
            else:
                print("[ERROR] runtime_worker not set")

        else:
            print("[SCALING] already at minimum workers")

    elif action == "restart_worker":
        print("[ACTION EXECUTOR] restarting worker...")
