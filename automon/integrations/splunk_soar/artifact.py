from automon.log import Logging

from .datatypes import AbstractDataType

log = Logging('Artifact', level=Logging.CRITICAL)


class Artifact(AbstractDataType):
    name: str = None
    container: int = None
    id: int = None

    def __repr__(self):
        if self.name:
            return self.name
        return f'{self.to_dict()}'
