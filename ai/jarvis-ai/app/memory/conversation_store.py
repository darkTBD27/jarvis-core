conversation = []

MAX_HISTORY = 50


def add_entry(user, response):

    conversation.append({

        "user": user,

        "response": response

    })

    if len(conversation) > MAX_HISTORY:

        conversation.pop(0)


def get_history():

    return conversation
    
    
def get_conversation():

    return get_history()
