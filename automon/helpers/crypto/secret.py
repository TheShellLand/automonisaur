import os


def new_secret_key():
    return os.urandom(16)
