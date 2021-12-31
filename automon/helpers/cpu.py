import psutil

from automon.log import Logging

log = Logging('cpu', level=Logging.DEBUG)


def cpu_usage(max_cpu_percentage=80):
    """Limit max cpu usage
    """
    if psutil.cpu_percent() < max_cpu_percentage:
        log.debug(f'[{cpu_usage.__name__}] {psutil.cpu_percent()}%')
        return True
    else:
        log.debug(f'[{cpu_usage.__name__}] {psutil.cpu_percent()}%')
        return False
