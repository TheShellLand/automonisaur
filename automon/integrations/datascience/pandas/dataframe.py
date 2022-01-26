import pandas

from automon.log import Logging


def DataFrame(*args, **kwargs) -> pandas.DataFrame:
    log = Logging('DataFrame', level=Logging.ERROR)
    df = pandas.DataFrame(*args, **kwargs)
    log.debug(df)
    return df
