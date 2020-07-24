import neo4j

from urllib.parse import urlencode
from datetime import datetime, timezone
from neo4j import GraphDatabase

from automon.log.logger import Logging
from automon.integrations.neo4j.config import Neo4jConfig
from automon.helpers.assertions import assert_label

log = Logging(__name__, Logging.DEBUG)


class Neo4jWrapper:
    """Neo4j wrapper"""

    def __init__(self, config: Neo4jConfig = None) -> neo4j:

        self.config = config if isinstance(config, Neo4jConfig) else Neo4jConfig()

        self.user = self.config.user
        self.password = self.config.password
        self.hosts = self.config.hosts

        for server in self.hosts:
            try:
                self.neo4j = GraphDatabase.driver(server, auth=(self.user, self.password))
                self.driver = self.neo4j
                log.info(f'Connected to neo4j server: {server}')
            except:
                self.neo4j = None
                log.error(f'Cannot connect to neo4j server: {server}')
        else:
            self.neo4j = None

    def _http_header(self, headers) -> dict:
        # [print(x) for x in auth.request_headers(request)]

        # token = helper_brain.hash_key(sorted([x for x in headers]))

        args = dict(
            blob=sorted(headers),
            label='Headers'
        )

        return self._prepare_dict(**args)

    def _prepare_dict(self, blob: dict) -> dict:
        """All inputs first needs to dicts"""
        try:
            return dict(blob)
        except:
            return dict(raw=urlencode(blob))

    def _consolidate(self, query: list) -> list:
        """Join cypher queries list into a string"""
        return '\n'.join(query).strip()

    def _send(self, cypher: str) -> GraphDatabase.driver:
        """This is the query that will be run on the database. So make sure by the time it
        gets to this function all prior checks have passed. Also, create a last check in
        this function for general cypher query-ness"""

        if self.neo4j is None:
            return

        with self.neo4j.session() as session:
            results = session.run(cypher)

        log.debug(f'Cypher: {cypher}')
        log.debug(f'Results: {results}')

        # TODO: print records from cypher response
        # for record in results:
        #     for value in record._values:
        #         for props in value.properties:
        #             print(props, value.properties[props])

        return results

    def send_data(self, label, data):
        """Just take the entry and put it into the database to be parsed later"""

        timestamp_date = datetime.now(tz=timezone.utc).isoformat()
        label = assert_label(label)

        node = 'NODE'
        dict_blob = self._prepare_dict(data)

        # cypher_assertions = []
        # TODO: find a way to check if assertion has already been made
        # query = 'CREATE CONSTRAINT ON ( {node} {label} ) ASSERT {node}.raw IS UNIQUE'
        # query = query.format(node=node, label=label)
        # cypher_assertions.append(query)  # Pre cypher query

        query = list()
        query.append(f'MERGE ( {node} {label} ')
        query.append('{')

        # iterate dict keys
        i = 0
        for key in dict_blob.keys():
            i = i + 1
            value = dict_blob[key]

            if i < len(dict_blob.keys()):
                query.append(f'`{key}`: {value},')
            else:
                query.append(f'`{key}`: {value}')

        query.append(' } )')

        # timestamp of first seen
        # query.append('ON CREATE SET {}.timestamp = "{}"'.format(node, timestamp_date))

        # timestamp of every time seen
        query.append('SET {}.timestamp = "{}"'.format(node, timestamp_date))
        query.append('RETURN *')

        final_cypher = self._consolidate(query)  # self._consolidate sets of queries into one single related query

        log.debug(final_cypher)

        return self._send(final_cypher)

    def create_relationship(self, cypher):
        """Create relationship"""
        log.debug(cypher)
        return self._send(cypher)
