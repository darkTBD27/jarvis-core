from inference.runtime_object import RUNTIME_ACCESS

def check_runtime_triggers():

    runtime = RUNTIME_ACCESS

    triggers = []


    if runtime.read("health") == "error":

        triggers.append("runtime_error")


    if runtime.read("queue_size") > 10:

        triggers.append("queue_pressure")


    if runtime.read("busy"):

        triggers.append("runtime_busy")


    return triggers


def run_automation(triggers):
    # Phase 4:
    # Automation ist deaktiviert (keine Actions, keine Writes)
    return None
