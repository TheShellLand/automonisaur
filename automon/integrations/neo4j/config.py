import os

from automon.log.logger import Logging
from automon.helpers.sanitation import Sanitation as S
from automon.log.logger import Logging

log = Logging(name=__name__, level=Logging.DEBUG)


class Neo4jConfig:
    def __init__(self):
        self._log = Logging(name=Neo4jConfig.__name__, level=Logging.ERROR)
        self.user = os.getenv('NEO4J_USER') or ''
        self.password = os.getenv('NEO4J_PASSWORD') or ''
        self.hosts = S.list_from_string(os.getenv('NEO4J_SERVERS')) or []

        if not self.user:
            self._log.error(f'NEO4J_USER not set')

        if not self.password:
            self._log.error(f'NEO4J_PASSWORD not set')

        if not self.hosts:
            self._log.error(f'NEO4J_SERVERS not set')
