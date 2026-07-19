import os
import traceback


def debug(log: str = '', level: int = 0, **kwargs) -> None:
    DEBUG = os.getenv('DEBUG')

    if not DEBUG:
        DEBUG = 0

    if DEBUG <= level:
        print(f'{log}', **kwargs)


def debug_str(log_list: list):
    log_list = [str(x) for x in log_list if x and x is not None]
    return ' :: '.join(log_list)


def debug_exception(error_context=None, log=None) -> Exception:
    try:
        tb = traceback.format_exc()
    except:
        tb = None

    if error_context is not None:
        error_context = [(k, v) for k, v in error_context.items()]
        error_context = [f'[CONTEXT] {k}={v}' for k, v in error_context]
        error_context = '\n'.join(error_context)

    if log is not None:
        raise Exception(f'{log=}\n\n{error_context}')

    if tb is not None:
        raise Exception(f'{error_context}\n\n{tb}')

    raise Exception(f'{error_context}')
