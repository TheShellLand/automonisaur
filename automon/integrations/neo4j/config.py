import os

from automon.log import Logging
from automon.helpers.sanitation import Sanitation as S

log = Logging(name=__name__, level=Logging.DEBUG)


class Neo4jConfig:
    def __init__(self, user: str = None,
                 password: str = None,
                 hosts: str = None,
                 encrypted: bool = None,
                 trust: bool = None):
        """Neo4j config
        """

        self._log = Logging(name=Neo4jConfig.__name__, level=Logging.ERROR)

        self.NEO4J_USER = user or os.getenv('NEO4J_USER') or ''
        self.NEO4J_PASSWORD = password or os.getenv('NEO4J_PASSWORD') or ''
        self.NEO4J_HOST = hosts or os.getenv('NEO4J_HOST') or ''

        self.encrypted = encrypted
        self.trust = trust

        if not self.NEO4J_USER: self._log.warn(f'missing NEO4J_USER')
        if not self.NEO4J_PASSWORD: self._log.warn(f'missing NEO4J_PASSWORD')
        if not self.NEO4J_HOST: self._log.warn(f'missing NEO4J_HOST')

    def __repr__(self):
        return f'{self.__dict__}'
