import hashlib


def hash_key(blob):
    """ Make a hash key """

    return hashlib.md5(str(blob).encode()).digest().hex()
