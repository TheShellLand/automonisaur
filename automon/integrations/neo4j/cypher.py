import re

from urllib.parse import urlencode
from datetime import datetime, timezone

from automon.log.logger import Logging

log = Logging(__name__, Logging.DEBUG)


class Cypher:

    def __init__(self):
        self.cypher = []
        self._node = 'Node'

    def __repr__(self):
        return self.consolidate()

    def start(self, data: dict, node: str = None, label: str = ''):
        """alias to merge"""
        return self.merge(node=node, label=label, data=data)

    def merge(self, data: dict, node: str = None, label: str = ''):
        """Merge a node

        MERGE (Node :`human` { `name`: "finn" })
        ON CREATE SET Node.first_seen = "2021-02-25T03:19:47.438596+00:00"
        ON CREATE SET Node.first_seen_ts = timestamp()
        SET Node.last_seen = "2021-02-25T03:19:47.438901+00:00"
        SET Node.last_seen_ts = timestamp()
        RETURN *

        """
        node = node or self._node
        label = self.assert_label(label)
        self.cypher.append(f'MERGE ({node} {label} {{')
        self.dict_to_cypher(data)
        self._end()
        self.first_seen()
        self.last_seen()
        self._return_asterisk()

    def create(self, data: dict, node: str = None, label: str = ''):
        """Create a node"""
        node = node or self._node
        label = self.assert_label(label)
        self.cypher.append(f'CREATE ({node} {label} {{')
        self.dict_to_cypher(data)
        self._end()
        self.last_seen()
        self._return_asterisk()

    def unique(self, node: str = None, label: str = ''):
        node = node or self._node
        label = self.assert_label(label)
        self.cypher.append(f'UNIQUE ({node} {label} {{')

    def match(self, node: str, prop: str, value: str):
        """Match a node"""
        node = node or self._node
        # MATCH (n {name: 'Andy'})
        self.cypher.append(f'MATCH ({node} {{{prop}: "{value}"}})')

    def relationship(self, label: str, prop: str, value: str, other_prop: str,
                     other_value: str, relationship: str, other_label: str = None):
        """Create an A -> B relationship

        MATCH (a:Person), (b:Person)
        WHERE a.name = 'A' AND b.name = 'B'
        CREATE (a)-[r:RELTYPE]->(b)
        RETURN type(r)

        """

        label = self.assert_label(label)
        other_label = self.assert_label(other_label)
        relationship = self.assert_label(relationship)

        if not other_label:
            other_label = label

        self.cypher.append(f'MATCH (a{label}), (b{other_label})')
        self.cypher.append(
            f'WHERE a.{prop} = "{value}" AND b.{other_prop} = "{other_value}"')
        self.cypher.append(f'MERGE (a)-[r{relationship}]->(b)')
        self.cypher.append(f'RETURN type(r)')

    def _end(self):
        """End of cypher"""
        self.cypher.append('})')

    def _return_asterisk(self):
        self.cypher.append('RETURN *')

    def first_seen(self, node: str = None):
        """Node first_seen property"""
        node = node or self._node
        time = datetime.now(tz=timezone.utc).isoformat()
        # ON CREATE SET keanu.created = timestamp()
        self.cypher.append(f'ON CREATE SET {node}.first_seen = "{time}"')
        self.cypher.append(f'ON CREATE SET {node}.first_seen_ts = timestamp()')

    def last_seen(self, node: str = None):
        """Node last_seen property"""
        node = node or self._node
        time = datetime.now(tz=timezone.utc).isoformat()
        self.cypher.append(f'SET {node}.last_seen = "{time}"')
        self.cypher.append(f'SET {node}.last_seen_ts = timestamp()')

    def on_create_set(self):
        # timestamp of first seen
        # query.append('ON CREATE SET {}.timestamp = "{}"'.format(node, timestamp_date))
        return

    # @staticmethod
    # def begin():
    #     return '{'

    def dict_to_cypher(self, obj: dict):
        """Dict to cypher

        must be { `key`: 'value' }
        """

        obj = self.prepare_dict(obj)
        cypher = []
        i = 1
        for key in obj.keys():
            value = obj.get(key)
            query = f'`{key}`: "{value}"'

            if i < len(obj.keys()):
                cypher.append(query + ',')
            else:
                cypher.append(query)
            i += 1

        self.cypher.append(' '.join(cypher))

    def consolidate(self) -> str:
        """Join cypher queries list into a string"""
        return ' '.join(self.cypher).strip()

    @staticmethod
    def prepare_dict(blob: dict) -> dict:
        """All inputs first needs to dicts"""
        try:
            return dict(blob)
        except Exception as _:
            return dict(raw=urlencode(blob))

    @staticmethod
    def assert_label(label: str) -> str:
        """Make sure neo4j label is formatted correctly"""

        if not label:
            return ''

        if re.search('[:]', label):
            log.error(f"Invalid label '{label}': Remove the colon from the label")
            label = label.replace(':', '')

        if not re.search('[a-zA-Z]', label[0]):  # First letter of a label must be a letter
            log.error(f"Invalid label '{label}': First character of Neo4j :LABEL must be a letter")
        else:
            return f':`{label}`'  # :`Label`

    def delete_all(self):
        """Delete all nodes and relationships"""
        self.cypher.append(f'MATCH (n) DETACH DELETE n')

    def delete_node(self, prop: str, value: str, node: str = None):
        """Delete all matching nodes and its relationships"""
        node = node or self._node
        # MATCH (n {name: 'Andy'})
        # DETACH DELETE n
        self.match(prop=prop, value=value, node=node)
        self.cypher.append(f'DETACH DELETE {node}')
