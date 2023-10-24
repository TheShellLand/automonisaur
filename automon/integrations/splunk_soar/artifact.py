from automon.log import logger

from .datatypes import AbstractDataType

log = logger.logging.getLogger(__name__)
log.setLevel(logger.CRITICAL)


class Artifact(AbstractDataType):
    name: str = None
    container: int = None
    id: int = None

    def __repr__(self):
        if self.name:
            return self.name
        return f'{self.to_dict()}'
