from automon.log import Logging

from .datatypes import AbstractDataType

log = Logging(name='Asset', level=Logging.DEBUG)


class Asset(AbstractDataType):
    def __init__(self, asset: dict = {}):
        self.__dict__.update(asset)
