import os


def debug(log: str = '', level: int = 0, **kwargs) -> None:
    DEBUG = os.getenv('DEBUG')

    if not DEBUG:
        DEBUG = 0

    if DEBUG <= level:
        print(f'{log}', **kwargs)
