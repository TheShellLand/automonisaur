import pandas

from automon import Logging


def Series(*args, **kwargs) -> pandas.Series:
    log = Logging('Series', level=Logging.ERROR)
    s = pandas.Series(*args, **kwargs)
    log.debug(s)
    return s
