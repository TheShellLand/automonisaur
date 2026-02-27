DEBUG_LEVEL = 1


def debug(log: str, level: int = 1, **kwargs):
    global DEBUG_LEVEL

    if 'DEBUG_LEVEL' not in globals():
        DEBUG_LEVEL = 1

    if DEBUG_LEVEL >= level:
        print(f"{log}", **kwargs)
