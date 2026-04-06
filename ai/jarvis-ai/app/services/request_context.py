import uuid
import time


class RequestContext:

    def __init__(self, prompt=None, request_id=None, intent=None, conversation_id=None):

        if request_id:
            self.request_id = request_id
        else:
            self.request_id = self._generate_id()

        self.created_at = time.time()

        self.prompt = prompt
        self.intent = intent

        self.conversation_id = conversation_id

        self.status = "created"

        self.execution_path = None

        self.metadata = {}


    def _generate_id(self):

        return str(uuid.uuid4())[0:8]


    def set_status(self, status):

        self.status = status


    def set_intent(self, intent):

        self.intent = intent


    def set_execution_path(self, path):

        self.execution_path = path


    def add_meta(self, key, value):

        self.metadata[key] = value


    def to_dict(self):

        return {

            "request_id": self.request_id,
            "conversation_id": self.conversation_id,
            "status": self.status,
            "created_at": self.created_at,
            "intent": self.intent,
            "execution_path": self.execution_path,
            "metadata": self.metadata,

        }
