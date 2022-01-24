import neo4j
import asyncio

from neo4j import GraphDatabase
from queue import Queue

from automon.log import Logging
from automon.log.logger import logging
from automon.integrations.neo4j.cypher import Cypher

from .config import Neo4jConfig
from .results import Results

logging.getLogger('neo4j').setLevel(logging.ERROR)
log = Logging(__name__, Logging.DEBUG)


class Neo4jAsyncClient:

    def __init__(self,
                 user: str = None,
                 password: str = None,
                 hosts: list or str = None,
                 config: Neo4jConfig = None) -> neo4j:
        """Neo4j async client

        :param config: Neo4jConfig
        :param user: str
        :param password: str
        :param hosts: list
        :param encrypted: bool
        """
        self._log = Logging(Neo4jAsyncClient.__name__, Logging.DEBUG)

        self.config = config or Neo4jConfig(
            user=user,
            password=password,
            hosts=hosts
        )

        self.client = self._client()
        self.driver = self.client
        self.session = self.client.session()
        self.connected = self.isConnected()
        self.cypher = Queue()

    def __repr__(self):
        return f'{self.__dict__}'

    def _check_connection(self):
        if self.client:
            return True
        return False

    def _client(self):
        try:
            client = GraphDatabase.driver(
                uri=self.config.NEO4J_HOST,
                auth=(self.config.NEO4J_USER, self.config.NEO4J_PASSWORD))
            log.info(f'Connected to neo4j server: {self.config.NEO4J_HOST}')
            return client

        except Exception as e:
            self._log.error(f'Cannot connect to neo4j server: {self.config.NEO4J_HOST}, {e}',
                            enable_traceback=False, raise_exception=True)

        return False

    def _consumer(self):
        return

    def _producer(self):
        return

    def isConnected(self):
        return self._check_connection()

    def run(self):
        """Send cyphers in queue"""
        try:
            while not self.cypher.empty():
                cypher = self.cypher.get_nowait()
                self._log.debug(f'cypher: {cypher}')
                self.session.run(cypher)
            return True
        except Exception as e:
            self._log.error(f'{e}')

        return False
