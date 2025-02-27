import neo4j
import asyncio

from neo4j import GraphDatabase
from queue import Queue

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.integrations.neo4jWrapper.cypher import Cypher

from .config import Neo4jConfig
from .results import Results

LoggingClient.logging.getLogger('neo4j').setLevel(logger.ERROR)
logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


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
            logger.info(f'Connected to neo4j server: {self.config.NEO4J_HOST}')
            return client

        except Exception as e:
            logger.error(f'Cannot connect to neo4j server: {self.config.NEO4J_HOST}, {e}')

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
                logger.debug(f'cypher: {cypher}')
                self.session.run(cypher)
            return True
        except Exception as e:
            logger.error(f'{e}')

        return False
