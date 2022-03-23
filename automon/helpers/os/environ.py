import os


def environ(env_var: str, default: any = None):
    env = os.getenv(env_var)
    if env:
        if f'{env}'.lower() == 'true':
            return True
        if f'{env}'.lower() == 'false':
            return False
        return f'{env}'.strip()
    return default
