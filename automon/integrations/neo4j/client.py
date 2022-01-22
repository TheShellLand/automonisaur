import neo4j
import logging

from neo4j import GraphDatabase

from automon.log import Logging
from automon.integrations.neo4j.cypher import Cypher
from automon.integrations.neo4j.config import Neo4jConfig
from automon.integrations.neo4j.helpers import Results
from automon.helpers.sanitation import Sanitation as S

logging.getLogger('neo4j').setLevel(logging.ERROR)
log = Logging(__name__, Logging.DEBUG)


class Neo4jClient:

    def __init__(self,
                 user: str = None,
                 password: str = None,
                 hosts: list or str = None,
                 config: Neo4jConfig = None) -> neo4j:
        """Neo4j client

        :param config: Neo4jConfig
        :param user: str
        :param password: str
        :param hosts: list
        :param encrypted: bool
        """
        self._log = Logging(Neo4jClient.__name__, Logging.DEBUG)

        self.config = config or Neo4jConfig(
            user=user,
            password=password,
            hosts=hosts
        )

        self.client = self._client()
        self.connected = self.isConnected()

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

    def _send(self, cypher: str or Cypher) -> GraphDatabase.driver:
        """Send cypher to server"""

        if not self.connected:
            return False

        if isinstance(cypher, Cypher):
            cypher = f'{cypher}'

        with self.client.session() as session:
            results = session.run(cypher)

        self._log.debug(f'{cypher}')
        self._log.debug(f'Results: {Results(results)}')

        return results

    def isConnected(self):
        return self._check_connection()

    def cypher(self, query: str):
        """Run a straight cypher query"""
        return self._send(S.strip(query))

    def create(self, data: dict, label: str = None, node: str = None):
        """Create a node"""

        cypher = Cypher()
        cypher.create(node=node, label=label, data=data)

        # self._log.debug(f'{final_cypher}')

        return self._send(cypher)

    def create_relationship(self, label: str, prop: str, value: str, other_prop: str,
                            other_value: str, relationship: str, other_label: str = None):
        """Create an A -> B relationship"""

        cypher = Cypher()
        cypher.relationship(
            label, prop, value, other_prop, other_value, relationship, other_label)

        self._log.debug(cypher)
        return self._send(cypher)

    def delete_all(self):
        """Delete all nodes and relationships"""
        cypher = Cypher()
        cypher.delete_all()
        return self._send(cypher)

    def delete_node(self, prop: str, value: str, node: str = None):
        """Delete all matching nodes and its relationships"""
        cypher = Cypher()
        cypher.delete_node(prop=prop, value=value, node=node)
        return self._send(cypher)

    def merge(self, data: dict, label: str = None, node: str = None):
        """Merge a node"""

        # cypher_assertions = []
        # TODO: find a way to check if assertion has already been made
        # query = 'CREATE CONSTRAINT ON ( {node} {label} ) ASSERT {node}.raw IS UNIQUE'
        # query = query.format(node=node, label=label)
        # cypher_assertions.append(query)  # Pre cypher query

        cypher = Cypher()
        cypher.merge(node=node, label=label, data=data)

        # self._log.debug(f'{final_cypher}')

        return self._send(cypher)

    def search(self, query: str):
        return
