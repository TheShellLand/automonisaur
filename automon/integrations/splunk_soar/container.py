import datetime

from automon import log

from .datatypes import AbstractDataType

logger = log.logging.getLogger(__name__)
logger.setLevel(log.CRITICAL)


class Container(AbstractDataType):
    artifact_count: int = None
    start_time: datetime = None
    id: int = None
    name: str = None

    def __repr__(self):
        if self.name:
            return f'{self.name}'
        return f'{self.id}'
