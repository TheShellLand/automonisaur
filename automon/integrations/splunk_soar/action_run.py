from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, CRITICAL

from .datatypes import AbstractDataType

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(CRITICAL)


class ActionRun(AbstractDataType):
    container: int = None
    id: int = None

    def __repr__(self):
        if self.id:
            return f'{self.id}'
        return f'{self.to_dict()}'
