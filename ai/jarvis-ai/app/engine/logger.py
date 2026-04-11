import time

import logging

logger = logging.getLogger("jarvis")


def _get_request_id(request=None, request_id=None):

    if request:
        return request.request_id

    return request_id


def log_inference_start(prompt, request=None, request_id=None):

    rid = _get_request_id(request, request_id)

    if request:
        request.mark_processing()

    logger.info(f"[AI] START request | id={rid} | prompt_length={len(prompt)}")

    return time.time()


def log_inference_end(start_time, request=None, request_id=None):

    rid = _get_request_id(request, request_id)

    duration = round(time.time() - start_time,2)

    if request:
        request.mark_finished()

    logger.info(f"[AI] END request | id={rid} | duration={duration}s")


def log_inference_error(error, request=None, request_id=None):

    rid = _get_request_id(request, request_id)

    if request:
        request.mark_error()

    logger.info(f"[AI] ERROR | id={rid} | {error}")
