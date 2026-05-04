# VERIFY_MARKER: G6kfZa)c

import queue
import concurrent.futures
import atexit
import time
import os

from inference.events import emit_event

from config.runtime_config import MAX_QUEUE_SIZE

from engine.logger import logger


REQUEST_QUEUE = queue.PriorityQueue(maxsize=MAX_QUEUE_SIZE)

EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def shutdown_executor():

    try:

        EXECUTOR.shutdown(

            wait=False,
            cancel_futures=True

        )

        logger.info("[Jarvis] Executor shutdown complete")

    except Exception as e:

        logger.info("[Jarvis] Executor shutdown error:",e)


atexit.register(shutdown_executor)


def queue_full():

    return REQUEST_QUEUE.full()


def queue_size():

    return REQUEST_QUEUE.qsize()

# PHASE 1: offizieller externer Eintrittspunkt in den produktiven Runtime-Pfad
# Ab hier beginnt der kontrollierte Backbone-Eintritt (Queue-Eintrittspuffer)
def enqueue_request(item):
    try:
        REQUEST_QUEUE.put(item)

        request_id = None
        if len(item) > 1 and len(item[1]) > 3:
            request_id = item[1][3]

        emit_event("queue_enqueue", {
            "size": REQUEST_QUEUE.qsize(),
            "request_id": request_id
        })

        return True

    except Exception:
        return False

# PHASE 1: exklusiver interner Übergabepunkt vom Eintrittspuffer in den Runtime-Kontrollpfad
# Ab hier endet Queue-Pufferung und aktiver Runtime-Kontrollfluss beginnt
def dequeue_request():
    try:
        if REQUEST_QUEUE.empty():
            return None

        item = REQUEST_QUEUE.get()

        request_id = None
        if len(item) > 1 and len(item[1]) > 3:
            request_id = item[1][3]

        emit_event("queue_dequeue", {
            "size": REQUEST_QUEUE.qsize(),
            "request_id": request_id
        })

        return item

    except Exception:
        return None


def queue_empty():

    return REQUEST_QUEUE.empty()


def _queue_items_snapshot():

    return list(REQUEST_QUEUE.queue)


def queued_ids():

    ids = []

    try:

        items = _queue_items_snapshot()

        for item in items:

            if len(item) > 1:

                payload = item[1]

                if len(payload) > 3:

                    ids.append(payload[3])

    except Exception:

        return []

    return ids


def get_queue_size():

    return REQUEST_QUEUE.qsize()


def executor_busy():

    return EXECUTOR._work_queue.qsize() > 0


def executor_queue_size():

    return EXECUTOR._work_queue.qsize()


def queue_pressure():

    try:

        return REQUEST_QUEUE.qsize() / MAX_QUEUE_SIZE

    except Exception:

        return 0


def snapshot_queue():
    try:
        items = _queue_items_snapshot()

        result = []

        for item in items:
            if len(item) > 1:
                payload = item[1]

                if len(payload) > 3:
                    result.append({
                        "priority": item[0],
                        "request_id": payload[3]
                    })

        return result

    except Exception:
        return []
