import os

from automon.log import logger
from automon.helpers.sanitation import Sanitation
from automon.helpers.osWrapper.environ import environ

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


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

        if not self.NEO4J_USER: log.error(f'missing NEO4J_USER')
        if not self.NEO4J_PASSWORD: log.error(f'missing NEO4J_PASSWORD')
        if not self.NEO4J_HOST: log.error(f'missing NEO4J_HOST')

    @property
    def is_ready(self) -> bool:
        if self.NEO4J_USER and self.NEO4J_PASSWORD and self.NEO4J_HOST:
            return True
        return False

    def __repr__(self):
        return f'{self.__dict__}'
