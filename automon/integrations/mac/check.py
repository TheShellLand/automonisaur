import sys


def os_is_mac():
    if sys.platform == 'darwin':
        return True
    return False
