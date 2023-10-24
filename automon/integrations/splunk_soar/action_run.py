from automon.log import logger

from .datatypes import AbstractDataType

log = logger.logging.getLogger(__name__)
log.setLevel(logger.CRITICAL)


class ActionRun(AbstractDataType):
    container: int = None
    id: int = None

    def __repr__(self):
        if self.id:
            return f'{self.id}'
        return f'{self.to_dict()}'
