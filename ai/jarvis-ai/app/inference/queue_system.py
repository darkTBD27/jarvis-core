import queue
import concurrent.futures
import atexit
import time
import os

from inference.runtime_state import *
from inference.metrics import *
from inference.events import emit_event

from config.runtime_config import MAX_QUEUE_SIZE


REQUEST_QUEUE = queue.PriorityQueue(maxsize=MAX_QUEUE_SIZE)

EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def shutdown_executor():

    try:

        EXECUTOR.shutdown(

            wait=False,
            cancel_futures=True

        )

        print("[Jarvis] Executor shutdown complete")

    except Exception as e:

        print("[Jarvis] Executor shutdown error:",e)


atexit.register(shutdown_executor)


def queue_full():

    return REQUEST_QUEUE.full()


def queue_size():

    return REQUEST_QUEUE.qsize()


def enqueue_request(item):

    try:

        REQUEST_QUEUE.put(item)

        return True

    except Exception:

        return False


def dequeue_request():

    try:

        if REQUEST_QUEUE.empty():

            return None

        return REQUEST_QUEUE.get()

    except Exception:

        return None


def queue_empty():

    return REQUEST_QUEUE.empty()


def queued_ids():

    ids = []

    try:

        items = list(REQUEST_QUEUE.queue)

        for item in items:

            if len(item) > 1:

                payload = item[1]

                if len(payload) > 3:

                    ids.append(payload[3])

    except Exception:

        return []

    return ids


def get_queue():

    return REQUEST_QUEUE


def get_executor():

    return EXECUTOR


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
