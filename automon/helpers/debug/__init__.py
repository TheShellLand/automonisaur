import os


def debug(log: str = '', level: int = 0, **kwargs) -> None:
    DEBUG = os.getenv('DEBUG')

    if not DEBUG:
        DEBUG = 0

    if DEBUG <= level:
        print(f'{log}', **kwargs)


def debug_str(log_list: list):
    log_list = [str(x) for x in log_list if x and x is not None]
    return ' :: '.join(log_list)
