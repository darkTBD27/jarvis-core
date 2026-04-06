INTENT_AI = "ai"

INTENT_SYSTEM = "system"

INTENT_STATUS = "status"

INTENT_MEMORY = "memory"

INTENT_TOOL = "tool"

INTENT_HELP = "help"

INTENT_CLEAR = "clear"


SYSTEM_COMMANDS = {

    "status":INTENT_STATUS,

    "memory":INTENT_MEMORY,

    "help":INTENT_HELP,

    "clear":INTENT_CLEAR

}


def get_intent(prompt):

    if not prompt:
        return INTENT_AI


    text = prompt.strip().lower()


    if text.startswith("tool:"):
        return INTENT_TOOL


    if text in SYSTEM_COMMANDS:
        return INTENT_SYSTEM


    return INTENT_AI


def get_system_command(prompt):

    if not prompt:
        return None


    text = prompt.strip().lower()


    return SYSTEM_COMMANDS.get(text)


def is_system_intent(prompt):

    return get_intent(prompt) == INTENT_SYSTEM
