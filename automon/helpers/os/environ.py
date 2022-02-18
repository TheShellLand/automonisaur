import os


def environ(env_var: str, default: any = None):
    if os.getenv(env_var):
        return os.getenv(env_var)
    return default
