from automon.log import Logging

from .datatypes import AbstractDataType

log = Logging('Artifact', level=Logging.CRITICAL)


class Artifact(AbstractDataType):
    name: str
    container: int
    id: int

    def __init__(self, artifact: dict = {}):
        self.container = None
        self.id = None
        self.name = None
        self.__dict__.update(artifact)

    def __repr__(self):
        return self.name
