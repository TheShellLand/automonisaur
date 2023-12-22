from automon import log

from .datatypes import AbstractDataType

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class Asset(AbstractDataType):
    def __init__(self, asset: dict = {}):
        self.__dict__.update(asset)
