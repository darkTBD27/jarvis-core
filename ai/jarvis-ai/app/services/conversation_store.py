import threading


MAX_MESSAGES = 20


class ConversationStore:

    def __init__(self):

        self.lock = threading.Lock()

        self.conversations = {}


    def add_message(self, conversation_id, role, content):

        if not conversation_id:
            return

        with self.lock:

            if conversation_id not in self.conversations:

                self.conversations[conversation_id] = []

            self.conversations[conversation_id].append({

                "role": role,
                "content": content

            })

            # LIMIT HISTORY

            if len(self.conversations[conversation_id]) > MAX_MESSAGES:

                self.conversations[conversation_id].pop(0)


    def get_history(self, conversation_id):

        if not conversation_id:
            return []

        with self.lock:

            return self.conversations.get(

                conversation_id,
                []

            )[-MAX_MESSAGES:].copy()


    def clear(self, conversation_id):

        with self.lock:

            if conversation_id in self.conversations:

                del self.conversations[conversation_id]
