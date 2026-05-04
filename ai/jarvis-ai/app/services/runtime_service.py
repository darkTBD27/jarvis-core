# VERIFY_MARKER: VRHM3{zQ

from inference.queue_system import enqueue_request

import uuid

# PHASE 5: externer Service-Einstieg oberhalb des Runtime-Kerns
# Service darf Requests einspeisen, bleibt aber isolierter Aufrufer außerhalb des Runtime-Kontrollpfads
def run(prompt, request_id=None):

    if not request_id:

        request_id = str(uuid.uuid4())

    from inference.events import emit_event

    emit_event("runtime_run_requested", {
        "request_id": request_id,
        "mode": "manual_observation"
    })

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
