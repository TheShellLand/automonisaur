import logging

from urllib.parse import urlencode
from datetime import datetime, timezone
from neo4j import GraphDatabase

from automon.helpers.assertions import assert_label


# logging.basicConfig(level=DEBUG)


class neo4j_wrapper:
    """Neo4j wrapper
    
    """

    def __init__(self, neo4j_config):

        self.user = neo4j_config.user
        self.password = neo4j_config.password
        self.servers = neo4j_config.servers

        for server in self.servers:
            try:
                self.driver = GraphDatabase.driver(server, auth=(self.user, self.password))
                logging.info('Connected to neo4j server: {}'.format(server))
            except:
                self.driver = None
                logging.error('Cannot connect to neo4j server: {}'.format(server))

    def _prepare_dict(self, blob):
        """All inputs first needs to dicts
    
        """
        try:
            return dict(blob)
        except:
            return dict(raw=urlencode(blob))

    def _consolidate(self, query):
        """Join cypher queries list into a string

        """
        return '\n'.join(query).strip()

    def _send(self, cypher):
        """This is the query that will be run on the database. So make sure by the time it
        gets to this function all prior checks have passed. Also, create a last check in
        this function for general cypher query-ness

        """
        with self.driver.session() as session:
            results = session.run(cypher)

        logging.debug('Cypher: {}'.format(cypher))
        logging.debug('Results: {}'.format(results))

        # TODO: print records from cypher response
        # for record in results:
        #     for value in record._values:
        #         for props in value.properties:
        #             print(props, value.properties[props])

        return results

    def send_data(self, label, data):
        """Just take the entry and put it into the database to be parsed later
    
        """

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
        query.append('MERGE ( {} {} '.format(node, label))
        query.append('{')

        # iterate dict keys
        i = 0
        for key in dict_blob.keys():
            i = i + 1
            value = dict_blob[key]

            if i < len(dict_blob.keys()):
                query.append('`{}`: {},'.format(key, value))
            else:
                query.append('`{}`: {}'.format(key, value))

        query.append(' } )')

        # timestamp of first seen
        # query.append('ON CREATE SET {}.timestamp = "{}"'.format(node, timestamp_date))

        # timestamp of every time seen
        query.append('SET {}.timestamp = "{}"'.format(node, timestamp_date))
        query.append('RETURN *')

        final_cypher = self._consolidate(query)  # self._consolidate sets of queries into one single related query

        logging.debug(final_cypher)

        return self._send(final_cypher)

    def create_relationship(self, cypher):
        """Create relationship

        """
        logging.debug(cypher)
        return self._send(cypher)
