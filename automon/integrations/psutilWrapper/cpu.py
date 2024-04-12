import psutil

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


def cpu_usage(max_cpu_percentage=80):
    """Limit max cpu usage
    """
    if psutil.cpu_percent() < max_cpu_percentage:
        logger.debug(f'[{cpu_usage.__name__}] {psutil.cpu_percent()}%')
        return True
    else:
        logger.debug(f'[{cpu_usage.__name__}] {psutil.cpu_percent()}%')
        return False
