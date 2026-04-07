import threading

from memory.conversation_store import conversations


MAX_MESSAGES = 20


class ConversationStore:

    def __init__(self):

        self.lock = threading.Lock()


    def add_message(self, conversation_id, role, content):

        if not conversation_id:
            return

        with self.lock:

            if conversation_id not in conversations:

                conversations[conversation_id] = []

            conversations[conversation_id].append({

                "role": role,
                "content": content

            })

            # LIMIT HISTORY

            if len(conversations[conversation_id]) > MAX_MESSAGES:

                conversations[conversation_id].pop(0)


    def get_history(self, conversation_id):

        if not conversation_id:
            return []

        with self.lock:

            return conversations.get(

                conversation_id,
                []

            )[-MAX_MESSAGES:].copy()


    def clear(self, conversation_id):

        with self.lock:

            if conversation_id in conversations:

                del conversations[conversation_id]
