import psutil

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


def cpu_usage(max_cpu_percentage=80):
    """Limit max cpu usage
    """
    if psutil.cpu_percent() < max_cpu_percentage:
        logger.debug(f'[{cpu_usage.__name__}] {psutil.cpu_percent()}%')
        return True
    else:
        logger.debug(f'[{cpu_usage.__name__}] {psutil.cpu_percent()}%')
        return False
