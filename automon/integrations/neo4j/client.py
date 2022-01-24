import neo4j
import logging

from neo4j import GraphDatabase
from queue import Queue

from automon.log import Logging
from automon.integrations.neo4j.cypher import Cypher

from .config import Neo4jConfig
from .results import Results

logging.getLogger('neo4j').setLevel(logging.ERROR)


class Neo4jClient:

    def __init__(self,
                 user: str = None,
                 password: str = None,
                 hosts: list or str = None,
                 config: Neo4jConfig = None) -> neo4j:
        """Neo4j client"""
        self._log = Logging(Neo4jClient.__name__, Logging.DEBUG)

        self._config = config or Neo4jConfig(
            user=user,
            password=password,
            hosts=hosts
        )

        self._client = self._client()

        if self._client:
            self._driver = self._client
            self._session = self._client.session()

        self._Cypher = Cypher()

        self.queue = Queue()
        self.cypher = None
        self.results = None

    def __repr__(self):
        return f'{self.__dict__}'

    def _client(self):
        try:
            client = GraphDatabase.driver(
                uri=self._config.NEO4J_HOST,
                auth=(self._config.NEO4J_USER, self._config.NEO4J_PASSWORD))
            self._log.info(f'Connected to neo4j server: {self._config.NEO4J_HOST}')
            return client

        except Exception as e:
            self._log.error(f'Cannot connect to neo4j server: {self._config.NEO4J_HOST}, {e}',
                            enable_traceback=False, raise_exception=False)

        return False

    def _send(self, cypher: str or Cypher) -> GraphDatabase.driver:
        """Send cypher to server"""

        if not self.isConnected():
            return False

        if isinstance(cypher, Cypher):
            cypher = self._Cypher.consolidate()

        self.cypher = cypher

        return self.run()

    def build_cypher(self, query: str):
        """Build a cypher"""
        self.cypher += query

    def create(self, prop: str, value: str):
        cypher = self._Cypher.create(prop=prop, value=value)
        self.cypher = cypher
        return self.run()

    def create_node(self, data: dict, label: str = None, **kwargs):
        """Create a node"""
        cypher = self._Cypher.create_dict(label=label, data=data, **kwargs)
        self.cypher = cypher
        return self.run()

    def create_relationship(self, label: str,
                            prop: str,
                            value: str,
                            other_prop: str,
                            other_value: str,
                            relationship: str,
                            other_label: str = None):
        """Create an A -> B relationship"""

        self._Cypher.relationship(
            label, prop, value, other_prop, other_value, relationship, other_label)

        self._log.debug(self._Cypher)
        return self._send(self._Cypher)

    def cypher_run(self, query: str):
        """Run a straight cypher query"""
        self.cypher = query
        return self.run()

    def delete_all(self):
        """Delete all nodes and relationships"""
        self.cypher = self._Cypher.delete_all()
        return self.run()

    def delete_match(self, prop: str, value: str, node: str = None):
        """Delete all matching nodes and its relationships"""
        cypher = self._Cypher.delete_node(prop=prop, value=value, node=node)
        self.cypher = cypher
        return self.run()

    def isConnected(self):
        if self._client:
            return True
        return False

    def merge(self, prop: str, value: str):
        cypher = self._Cypher.merge(prop=prop, value=value)
        self.cypher = cypher
        return self.run()

    def merge_dict(self, data: dict, label: str = None, **kwargs):
        """Merge a node"""

        # cypher_assertions = []
        # TODO: find a way to check if assertion has already been made
        # query = 'CREATE CONSTRAINT ON ( {node} {label} ) ASSERT {node}.raw IS UNIQUE'
        # query = query.format(node=node, label=label)
        # cypher_assertions.append(query)  # Pre cypher query

        cypher = self._Cypher.merge_dict(label=label, data=data)
        self.cypher = cypher
        return self.run()

    def merge_node(self, data: dict, label: str = None, **kwargs):
        """Merge a node"""

        # cypher_assertions = []
        # TODO: find a way to check if assertion has already been made
        # query = 'CREATE CONSTRAINT ON ( {node} {label} ) ASSERT {node}.raw IS UNIQUE'
        # query = query.format(node=node, label=label)
        # cypher_assertions.append(query)  # Pre cypher query

        cypher = self._Cypher.merge_dict(label=label, data=data)

        # self._log.debug(f'{final_cypher}')

        return self._send(cypher)

    def run(self, cypher=None):
        """Send cypher"""
        try:
            cypher = self.cypher
            response = self._session.run(cypher)
            self.results = Results(response)

            self._log.info(f'cypher: {cypher}')
            self._log.debug(f'Results: {self.results}')

            return True
        except Exception as e:
            self._log.error(f"{e}", enable_traceback=False, raise_exception=True)

        return False

    def search(self, query: str):
        return NotImplemented
