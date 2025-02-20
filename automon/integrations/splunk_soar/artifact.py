from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, CRITICAL

from .datatypes import AbstractDataType

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(CRITICAL)


class Artifact(AbstractDataType):
    name: str = None
    container: int = None
    id: int = None

    def __repr__(self):
        if self.name:
            return self.name
        return f'{self.to_dict()}'
