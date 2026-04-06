from config.system_prompt import SYSTEM_PROMPT

MAX_CONVERSATION = 5


def build_prompt(user_prompt, memory_context=None, memory_enabled=True, conversation_history=None):

    memory_text = ""

    if memory_enabled and memory_context:

        valid_items = {
            k: v for k, v in memory_context.items()
            if v not in [None, "None", {}, "", []]
        }

        if valid_items:

            memory_text = "\nSystem Memory:\n"

            for key, value in valid_items.items():

                if isinstance(value, dict):

                    val = value.get("value")

                    if val not in [None, "None", ""]:

                        memory_text += f"{key}: {val}\n"

                else:

                    memory_text += f"{key}: {value}\n"


    conversation_text = ""

    if conversation_history:

        conversation_text = "\nConversation History:\n"

        for entry in conversation_history[-MAX_CONVERSATION:]:

            role = entry.get("role","")
            content = entry.get("content","")

            if role and content:

                conversation_text += f"{role}: {content[:200]}\n"


    final_prompt = (
        SYSTEM_PROMPT
        + "\n"
        + memory_text
        + "\n"
        + conversation_text
        + "\nAnfrage:\n"
        + user_prompt.strip()
        + "\n\nJarvis Antwort:"
    )

    return final_prompt
