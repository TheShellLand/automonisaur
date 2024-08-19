import pandas

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


def Series(*args, **kwargs) -> pandas.Series:
    s = pandas.Series(*args, **kwargs)
    logger.debug(s)
    return s
