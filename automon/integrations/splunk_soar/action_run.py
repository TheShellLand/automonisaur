from automon import log

from .datatypes import AbstractDataType

logger = log.logging.getLogger(__name__)
logger.setLevel(log.CRITICAL)


class ActionRun(AbstractDataType):
    container: int = None
    id: int = None

    def __repr__(self):
        if self.id:
            return f'{self.id}'
        return f'{self.to_dict()}'
