store = {}


def memory_set(key, value):

    store[key] = value

    return True


def memory_get(key):

    if key in store:

        return store[key]

    return None


def memory_delete(key):

    if key in store:

        del store[key]

        return True

    return False


def memory_list():

    return store
