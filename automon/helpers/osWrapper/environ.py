import os


def environ(env_var: str, default: any = None) -> bool or str or None:
    """Get environment variable, else return default"""
    env = os.getenv(env_var)
    if env:
        if f'{env}'.lower() == 'true':
            return True
        if f'{env}'.lower() == 'false':
            return False
        return f'{env}'.strip()
    return default
