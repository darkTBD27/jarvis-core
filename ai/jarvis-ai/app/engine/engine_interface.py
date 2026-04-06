from services.inference_request import InferenceRequest

from inference.inference import run_inference, inference_status
from inference.inference import get_request_status

from inference.inference import cancel_request

from inference.inference import retry_request


def run_engine(request: InferenceRequest):

    if not isinstance(request, InferenceRequest):
        raise ValueError("invalid request")

    request.mark_processing()

    try:

        result = run_inference(

            request.prompt,

            max_tokens=request.max_tokens,

            temperature=request.temperature,

            request_id=request.request_id,

            priority=False

        )

        if result.get("error"):

            request.mark_error()

        elif result.get("status") == "timeout":

            request.mark_error()

        else:

            if request.status != "finished":
                request.mark_finished()

        result["status"] = request.status

        return result

    except Exception:

        request.mark_error()

        raise


def get_engine_status():

    return inference_status()
    

def get_request(request_id):

    return get_request_status(request_id)


def cancel(request_id):

    cancel_request(request_id)

    return {

        "cancelled": True,
        "request_id": request_id

    }


def retry(request_id):

    return retry_request(request_id)
