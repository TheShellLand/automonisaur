from automon.helpers.debug import debug_exception


def is_true(text: str) -> bool | None:
    if 'true' in str(text).lower():
        return True
    if 'false' in str(text).lower():
        return False
    # raise debug_exception(locals(), 'neither true or false')


def is_false(text: str) -> bool | None:
    if 'false' in str(text).lower():
        return True
    if 'true' in str(text).lower():
        return False
    # raise debug_exception(locals(), 'neither true or false')
