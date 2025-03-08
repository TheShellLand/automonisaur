import hashlib


class Hashlib:

    @staticmethod
    def hash_key(blob):
        """ Make a hash key """

        return hashlib.md5(str(blob).encode()).digest().hex()

    @staticmethod
    def md5(blob):
        return Hashlib.hash_key(blob)
