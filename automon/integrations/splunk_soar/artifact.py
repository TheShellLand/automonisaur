from automon import log

from .datatypes import AbstractDataType

logger = log.logging.getLogger(__name__)
logger.setLevel(log.CRITICAL)


class Artifact(AbstractDataType):
    name: str = None
    container: int = None
    id: int = None

    def __repr__(self):
        if self.name:
            return self.name
        return f'{self.to_dict()}'
