import os
import inspect
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


def debug_exception(log=None) -> Exception:
    frame = inspect.currentframe()

    try:
        caller_frame = frame.f_back
        error_context = caller_frame.f_locals.copy()

        context = [
            f'[CONTEXT] {key}={value!r}'
            for key, value in error_context.items()
        ]

        context = '\n'.join(context)
        tb = traceback.format_exc()

        if log is not None:
            raise Exception(
                f'\n\nlog={log!r}'
                f'\n\n{context}'
                f'\n\n{tb}'
            )

        raise Exception(
            f'\n\n{context}'
            f'\n\n{tb}'
        )

    finally:
        del frame


def debug_locals():
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    error_context = caller_frame.f_locals.copy()
    return error_context
