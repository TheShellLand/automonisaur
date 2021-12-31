import re
from ast import literal_eval

from automon.log import Logging

log = Logging(__name__, Logging.DEBUG)


def make_tuple(obj: str) -> tuple:
    """Return a tuple from a string"""

    return literal_eval(obj)


def assert_tuple(obj: tuple or not tuple) -> bool:
    """Make sure it is a tuple"""

    if isinstance(obj, tuple):
        return True
    return False


def assert_dict(obj):
    """Make sure it is a dict"""

    try:
        if getattr(obj, 'fromkeys') \
                and getattr(obj, 'popitem') \
                and getattr(obj, 'setdefault') \
                and getattr(obj, 'update') \
                and getattr(obj, 'values'):
            return True
    except:
        return False


def assert_list(obj):
    """Make sure it is a list"""

    try:
        # isinstance(obj, list) and not isinstance(obj, str)
        if getattr(obj, 'append') and getattr(obj, 'sort') and getattr(obj, 'pop'):
            return True
    except:
        return False


def assert_string(obj):
    """Make sure it is a string"""

    try:
        # isinstance(obj, str)
        if getattr(obj, 'strip') and getattr(obj, 'split') and getattr(obj, 'rstrip'):
            return True
    except:
        return False
