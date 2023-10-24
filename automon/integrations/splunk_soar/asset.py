from automon.log import logger

from .datatypes import AbstractDataType

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class Asset(AbstractDataType):
    def __init__(self, asset: dict = {}):
        self.__dict__.update(asset)
