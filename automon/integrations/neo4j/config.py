import os

from automon.log import Logging
from automon.helpers.sanitation import Sanitation as S

log = Logging(name=__name__, level=Logging.DEBUG)


class Neo4jConfig:
    def __init__(self, user: str = None, password: str = None,
                 hosts: list = None, encrypted: bool = True):
        self._log = Logging(name=Neo4jConfig.__name__, level=Logging.ERROR)

        self.user = user or os.getenv('NEO4J_USER') or ''
        self.password = password or os.getenv('NEO4J_PASSWORD') or ''
        self.hosts = S.list_from_string(hosts) or \
                     S.list_from_string(os.getenv('NEO4J_SERVERS')) or []
        self.encrypted = encrypted

        if not self.user:
            self._log.warn(f'missing NEO4J_USER')

        if not self.password:
            self._log.warn(f'missing NEO4J_PASSWORD')

        if not self.hosts:
            self._log.warn(f'missing NEO4J_SERVERS')
