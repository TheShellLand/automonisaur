import pandas

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


def DataFrame(*args, **kwargs) -> pandas.DataFrame:
    df = pandas.DataFrame(*args, **kwargs)
    logger.debug(df)
    return df
