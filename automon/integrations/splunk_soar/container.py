import datetime

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, CRITICAL

from .datatypes import AbstractDataType

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(CRITICAL)


class Container(AbstractDataType):
    artifact_count: int = None
    start_time: datetime = None
    id: int = None
    name: str = None

    def __repr__(self):
        if self.name:
            return f'{self.name}'
        return f'{self.id}'
