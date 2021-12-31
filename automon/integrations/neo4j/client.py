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

    def __init__(self, config: Neo4jConfig = None, user: str = None,
                 password: str = None, hosts: list or str = None,
                 encrypted: bool = None) -> neo4j:
        """Neo4j client

        :param config: Neo4jConfig
        :param user: str
        :param password: str
        :param hosts: list
        :param encrypted: bool
        """
        self._log = Logging(Neo4jClient.__name__, Logging.DEBUG)

        self.config = config or Neo4jConfig()
        self.user = user or self.config.user
        self.password = password or self.config.password
        self.hosts = S.list_from_string(hosts) or self.config.hosts
        self.encrypted = encrypted or self.config.encrypted

        self.client = self._client(self.hosts)
        self.driver = self.client
        self.connected = self._check_connection()

    def _client(self, hosts: list):
        for server in hosts:
            try:
                client = GraphDatabase.driver(server, auth=(self.user, self.password), encrypted=self.encrypted)
                log.info(f'Connected to neo4j server: {server}')
                return client

            except Exception as e:
                self._log.error(f'Cannot connect to neo4j server: {server}, {e}', enable_traceback=False)
        return False

    def _check_connection(self):
        if self.client:
            return True
        return False

    def _send(self, cypher: str or Cypher) -> GraphDatabase.driver:
        """Send cypher to server"""

        if not self.connected:
            return False

        if isinstance(cypher, Cypher):
            cypher = f'{cypher}'

        with self.driver.session() as session:
            results = session.run(cypher)

        self._log.debug(f'{cypher}')
        self._log.debug(f'Results: {Results(results)}')

        return results

    def cypher(self, query: str):
        """Run a straight cypher query"""
        return self._send(S.strip(query))

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

    def search(self, query: str):
        return

    def __repr__(self):
        return f'{self.hosts}'
