conversations = {}

MAX_HISTORY = 50


def add_entry(conversation_id, user, response):

    if conversation_id not in conversations:

        conversations[conversation_id] = []

    conversations[conversation_id].append({

        "user": user,

        "response": response

    })

    if len(conversations[conversation_id]) > MAX_HISTORY:

        conversations[conversation_id].pop(0)


def get_history(conversation_id):

    return conversations.get(conversation_id,[])


def get_conversation(conversation_id):

    return get_history(conversation_id)
