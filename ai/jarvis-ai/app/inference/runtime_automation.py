from inference.runtime_object import get_runtime


def check_runtime_triggers():

    runtime = get_runtime()

    triggers = []


    if runtime.health == "error":

        triggers.append("runtime_error")


    if runtime.queue_size > 10:

        triggers.append("queue_pressure")


    if runtime.busy:

        triggers.append("runtime_busy")


    return triggers


def run_automation(triggers):

    runtime = get_runtime()

    for trigger in triggers:

        if trigger == "runtime_error":

            runtime.metric_inc("automation_error_detected")

        if trigger == "queue_pressure":

            runtime.metric_inc("automation_queue_pressure")
