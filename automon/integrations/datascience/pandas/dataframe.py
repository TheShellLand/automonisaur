import pandas

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


def DataFrame(*args, **kwargs) -> pandas.DataFrame:
    df = pandas.DataFrame(*args, **kwargs)
    logger.debug(df)
    return df
