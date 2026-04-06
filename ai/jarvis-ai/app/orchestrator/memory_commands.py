from services.memory_service import MemoryService


class MemoryCommands:


    def __init__(self):

        self.memory = MemoryService()


    def set(self, data, request_id=None):

        if not isinstance(data, dict):

            return {

                "error": True,

                "message": "data must be dict"

            }

        key = data.get("key")

        value = data.get("value")

        return self.memory.set(key, value)


    def get(self, data, request_id=None):

        if isinstance(data, dict):

            key = data.get("key")

        else:

            key = data

        if isinstance(key, str):

            key = key.replace('"','').strip()

        return self.memory.get(key)


    def delete(self, data, request_id=None):

        if isinstance(data, dict):

            key = data.get("key")

        else:

            key = data

        if isinstance(key, str):

            key = key.replace('"','').strip()

        return self.memory.delete(key)


    def list(self, data=None, request_id=None):

        return self.memory.list()
