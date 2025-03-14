from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, CRITICAL

from .datatypes import AbstractDataType

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(CRITICAL)


class Vault(AbstractDataType):
    contains: list = None
    deleted: bool = None
    first_seen_time: str
    hash: str = None
    id: int = None
    meta: dict
    names: list = None
    size: int = None
    sources: list
    tags: list = None
    version: int

    def __repr__(self):
        if self.names:
            return f'{",".join(self.names)}'
        return f'{self.to_dict()}'

    @property
    def sha1(self):
        return self.hash
