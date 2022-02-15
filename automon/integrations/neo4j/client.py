import neo4j
import logging

from neo4j import GraphDatabase
from queue import Queue

from automon.log import Logging
from automon.integrations.neo4j.cypher import Cypher

from .config import Neo4jConfig
from .results import Results

logging.getLogger('neo4j').setLevel(logging.ERROR)
log = Logging('Neo4jClient', Logging.DEBUG)


class Neo4jClient:

    def __init__(self,
                 user: str = None,
                 password: str = None,
                 hosts: list or str = None,
                 config: Neo4jConfig = None) -> neo4j:
        """Neo4j client"""

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
        self.cypher = ''
        self.results = None

    def __repr__(self):
        return f'{self.__dict__}'

    def _client(self):
        try:
            client = GraphDatabase.driver(
                uri=self._config.NEO4J_HOST,
                auth=(self._config.NEO4J_USER, self._config.NEO4J_PASSWORD))
            log.info(f'Connected to neo4j server: {self._config.NEO4J_HOST}')
            return client

        except Exception as e:
            log.error(f'Cannot connect to neo4j server: {self._config.NEO4J_HOST}, {e}',
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

    def create(self, prop: str,
               value: str,
               label: str = None,
               node: str = None, **kwargs):
        """Create a node"""
        cypher = self._Cypher.create(prop=prop, value=value, node=node, label=label, **kwargs)
        self.cypher = cypher
        return self.run()

    def create_dict(self, prop: str,
                    value: str,
                    data: dict,
                    label: str = None,
                    node: str = None, **kwargs):
        """Create a node from dict"""
        cypher = self._Cypher.create_dict(prop=prop, value=value, label=label, node=node, data=data, **kwargs)
        self.cypher = cypher
        return self.run()

    def relationship(self,
                     A_node: str = 'A', A_label: str = None, A_prop: str = None, A_value: str = None,
                     B_node: str = 'B', B_label: str = None, B_prop: str = None, B_value: str = None,
                     WHERE: str = None, label: str = None, node: str = 'r', direction: str = '->'):
        """Create relationship between two existing nodes"""

        cypher = self._Cypher.relationship(
            A_node=A_node, A_label=A_label, A_prop=A_prop, A_value=A_value,
            B_node=B_node, B_label=B_label, B_prop=B_prop, B_value=B_value,
            WHERE=WHERE, label=label, node=node, direction=direction)

        self.cypher = cypher
        return self.run()

    def cypher_run(self, query: str):
        """Run a cypher query"""
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
        """Check if client is connected to server"""
        if self._client:
            return True
        return False

    def match(self, prop: str, value: str, node: str = None):
        cypher = self._Cypher.match(prop=prop, value=value, node=node)
        self.cypher = cypher
        return self.run()

    def merge(self, prop: str = None, value: str = None, node: str = None, label: str = ''):
        """Merge nodes"""
        cypher = self._Cypher.merge(prop=prop, value=value, node=node, label=label)
        self.cypher = cypher
        return self.run()

    def merge_dict(self, prop: str, value: str, data: dict, label: str = None, node: str = None, **kwargs):
        """Merge nodes from dict"""

        # cypher_assertions = []
        # TODO: find a way to check if assertion has already been made
        # query = 'CREATE CONSTRAINT ON ( {node} {label} ) ASSERT {node}.raw IS UNIQUE'
        # query = query.format(node=node, label=label)
        # cypher_assertions.append(query)  # Pre cypher query

        cypher = self._Cypher.merge_dict(prop=prop, value=value, label=label, data=data, node=node, **kwargs)
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

        # log.debug(f'{final_cypher}')

        return self._send(cypher)

    def run(self, cypher=None) -> bool:
        """Send the cypher query to the server"""
        if not self.isConnected():
            return False

        cypher = self.cypher

        try:
            response = self._session.run(cypher)
            self.results = Results(response)

            log.info(f'cypher: {cypher}')
            log.debug(f'Results: {self.results}')

            return True
        except Exception as e:
            log.error(f"{e}", enable_traceback=False, raise_exception=True)

        return False

    def search(self, prop: str, value: str, node: str = None):
        cypher = self._Cypher.match(prop=prop, value=value, node=node)
        cypher += self._Cypher.return_all()
        self.cypher = cypher
        return self.run()
