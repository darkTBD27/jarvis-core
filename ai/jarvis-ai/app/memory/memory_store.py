import json
import os

STORE_FILE = "memory_store.json"

MAX_MEMORY_ITEMS = 1000


store = {}


def load_store():

    global store

    if not os.path.exists(STORE_FILE):

        return

    try:

        with open(STORE_FILE,"r") as f:

            store = json.load(f)

        print("[MEMORY] loaded from disk")

    except Exception as e:

        print(f"[MEMORY ERROR] load failed {e}")
        

def save_store():

    try:

        tmp_file = STORE_FILE + ".tmp"

        with open(tmp_file,"w") as f:

            json.dump(store,f)

        os.replace(tmp_file, STORE_FILE)

    except Exception as e:

        print(f"[MEMORY ERROR] save failed {e}")
        
        
def memory_set(key, value):

    store[key] = value
    
    if len(store) > MAX_MEMORY_ITEMS:

        oldest_key = next(iter(store))

        del store[oldest_key]

    save_store()

    return True


def memory_get(key):

    if key in store:

        return store[key]

    return None


def memory_delete(key):

    if key in store:

        del store[key]

        save_store()

        return True

    return False


def memory_list():

    return store


load_store()
