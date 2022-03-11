from automon import Logging

from .datatypes import AbstractDataType

log = Logging('Artifact', level=Logging.CRITICAL)


class Artifact(AbstractDataType):
    def __init__(self, artifact: dict = {}):
        self.__dict__.update(artifact)
