import os

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.helpers.sanitation import Sanitation
from automon.helpers.osWrapper import environ

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class Neo4jConfig:
    def __init__(
            self, user: str = None,
            password: str = None,
            hosts: str = None,
            encrypted: bool = None,
            trust: bool = None):
        """Neo4j config
        """

        self.NEO4J_USER = user or environ('NEO4J_USER', '')
        self.NEO4J_PASSWORD = password or environ('NEO4J_PASSWORD', '')
        self.NEO4J_HOST = hosts or environ('NEO4J_HOST', '')

        self.encrypted = encrypted
        self.trust = trust

    @property
    def is_ready(self) -> bool:
        if self.NEO4J_USER and self.NEO4J_PASSWORD and self.NEO4J_HOST:
            return True
        if not self.NEO4J_USER:
            logger.error(f'missing NEO4J_USER')
        if not self.NEO4J_PASSWORD:
            logger.error(f'missing NEO4J_PASSWORD')
        if not self.NEO4J_HOST:
            logger.error(f'missing NEO4J_HOST')
        return False

    def __repr__(self):
        return f'{self.__dict__}'
