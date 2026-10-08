import pandas

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


def Series(*args, **kwargs) -> pandas.Series:
    s = pandas.Series(*args, **kwargs)
    logger.debug(s)
    return s
