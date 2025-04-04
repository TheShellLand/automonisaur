import os


def environ(env_var: str, default: any = None) -> bool or str or None:
    """Get environment variable, else return default"""
    env = os.getenv(env_var)
    if env:
        if f'{env}'.lower() == 'true':
            return True
        if f'{env}'.lower() == 'false':
            return False
        env = f'{env}'.strip()
        env = f'{env}'.strip("'")
        env = f'{env}'.strip('"')
        return env
    return default


def environ_list(env_var: str, delimiter: str = ',', default: list = []) -> list:
    """Get environment variable as comma-separated, else return default"""
    env = os.getenv(env_var)
    if env:
        env = env.split(delimiter)
        env = [str(x).strip() for x in env]
        env = [str(x).strip("'") for x in env]
        env = [str(x).strip('"') for x in env]
        return env
    return default


def environ_set(key: str, value):
    os.environ[key] = value
