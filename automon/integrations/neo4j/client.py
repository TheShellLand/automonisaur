import neo4j
import logging

from neo4j import GraphDatabase

from automon.log.logger import Logging
from automon.integrations.neo4j.cypher import Cypher
from automon.integrations.neo4j.config import Neo4jConfig
from automon.integrations.neo4j.helpers import Results
from automon.helpers.sanitation import Sanitation as S

logging.getLogger('neo4j').setLevel(logging.ERROR)
log = Logging(__name__, Logging.DEBUG)


class Neo4jClient:
    """Neo4j client"""

    def __init__(self, config: Neo4jConfig = None, user: str = None,
                 password: str = None, hosts: list = None,
                 encrypted: bool = None) -> neo4j:
        self._log = Logging(Neo4jClient.__name__, Logging.DEBUG)

        self.config = config or Neo4jConfig()
        self.user = user or self.config.user
        self.password = password or self.config.password
        self.hosts = S.list_from_string(hosts) or self.config.hosts
        self.encrypted = encrypted or self.config.encrypted

        for server in self.hosts:
            try:
                self.client = GraphDatabase.driver(
                    server, auth=(self.user, self.password),
                    encrypted=self.encrypted)

                self.driver = self.client
                self.connected = True
                log.info(f'Connected to neo4j server: {server}')
            except Exception as e:
                self.connected = False
                self._log.error(f'Cannot connect to neo4j server: {server}\t{e}',
                                enable_traceback=False)

    def __str__(self):
        return f'{self.hosts}'

    def _send(self, cypher: str) -> GraphDatabase.driver:
        """This is the query that will be run on the database. So make sure by the time it
        gets to this function all prior checks have passed. Also, create a last check in
        this function for general cypher query-ness"""

        if not self.connected:
            return False

        with self.driver.session() as session:
            results = session.run(cypher)

        self._log.debug(f'{cypher}')
        self._log.debug(f'Results: {Results(results)}')

        return results

    def cypher(self, query: str):
        return self._send(S.strip(query))

    def delete_all(self):
        return self._send(Cypher.delete_all())

    def merge(self, data: dict, label: str = None, node: str = None):
        """Just take the entry and put it into the database to be parsed later"""

        # cypher_assertions = []
        # TODO: find a way to check if assertion has already been made
        # query = 'CREATE CONSTRAINT ON ( {node} {label} ) ASSERT {node}.raw IS UNIQUE'
        # query = query.format(node=node, label=label)
        # cypher_assertions.append(query)  # Pre cypher query

        cypher = Cypher()
        cypher.merge(node=node, label=label)
        cypher.dict_to_cypher(data)
        cypher.end()
        cypher.timestamp()
        cypher.return_asterisk()

        final_cypher = cypher.consolidate()  # self._consolidate sets of queries into one single related query

        # self._log.debug(f'{final_cypher}')

        return self._send(final_cypher)

    def create_relationship(self, cypher):
        """Create relationship"""
        self._log.debug(cypher)
        return self._send(cypher)
