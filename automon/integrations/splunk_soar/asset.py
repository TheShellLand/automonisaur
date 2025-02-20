from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

from .datatypes import AbstractDataType

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class Asset(AbstractDataType):
    def __init__(self, asset: dict = {}):
        self.__dict__.update(asset)
