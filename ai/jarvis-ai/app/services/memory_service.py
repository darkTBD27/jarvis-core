from memory.memory_store import memory_set
from memory.memory_store import memory_get
from memory.memory_store import memory_delete
from memory.memory_store import memory_list

import time


class MemoryService:


    def set(self, key, value):

        if not key:

            raise ValueError("memory key empty")

        entry = {

            "value": value,

            "timestamp": round(time.time(),2)

        }

        memory_set(key, entry)

        return {

            "key": key,

            "stored": True

        }


    def get(self, key):

        if not key:

            raise ValueError("memory key empty")

        data = memory_get(key)

        if data is None:

            return {

                "found": False

            }

        return {

            "found": True,

            "key": key,

            "value": data

        }


    def delete(self, key):

        if not key:

            raise ValueError("memory key empty")

        result = memory_delete(key)

        return {

            "deleted": result

        }


    def list(self):

        return {

            "memory": memory_list()

        }
