from inference.queue_system import enqueue_request

from inference.runtime_object import get_runtime

import uuid


def run(prompt, request_id=None):

    if not request_id:

        request_id = str(uuid.uuid4())

    runtime = get_runtime()

    runtime.metric_inc("requests_total")

    enqueue_request(

        (

            False,

            (

                prompt,

                256,

                0.7,

                request_id

            )

        )

    )

    return {

        "queued": True,

        "request_id": request_id

    }


# TODO Phase 3 Execution Intelligence

#def cancel(request_id):

    #cancel_request(request_id)

    #return {

        #"error":False,

        #"data":{

            #"cancelled":request_id

        #}

    #}


# TODO Phase 3 Execution Intelligence

#def retry(request_id):

    #result = retry_request(request_id)

    #return {

        #"error":result.get("error",False),

        #"data":result

    #}


# TODO Phase 3 Execution Intelligence

#def request(request_id):

    #data = get_request_status(request_id)

    #return {

        #"error":False,

        #"data":data

    #}
