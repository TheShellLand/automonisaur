import re

from urllib.parse import urlencode
from datetime import datetime, timezone

from automon.log import Logging

log = Logging(name='Cypher', level=Logging.DEBUG)


class Node:

    def __init__(self,
                 node: str = None,
                 label: str = None,
                 prop: str = None,
                 value: str = None):
        """Basic Node

        ( node :`label` { `prop`: "value" } )
        """
        self.node = node
        self.label = Cypher.assert_label(label)
        self.prop = Cypher.assert_property(prop)
        self.value = value

        if self.prop and self.value:
            prop_val = f'{self.prop}: "{self.value}"'
        else:
            prop_val = ''

        self.cypher = f'( {self.node} {self.label} {{ {prop_val} }} )'

    def __repr__(self):
        return self.cypher


class Cypher:

    def __init__(self):
        self.cypher = None
        self.cypher_list = []

    def __repr__(self):
        return f'{self.cypher}'

    def add_property(self, prop: str, value: str, node: str = None) -> str:
        """add property

        return: Node.prop = "value"
        """
        prop = self.assert_property(prop)
        cypher = f'{node}.{prop} = "{value}"'
        return cypher

    @staticmethod
    def assert_label(label: str) -> str:
        """Make sure neo4j label is formatted correctly"""

        if not label:
            return ''

        if re.search('[:]', label):
            log.warn(f"Invalid label '{label}': Colon is not needed here")
            label = label.replace(':', '')

        if re.search('[`]', label):
            label = label.replace('`', '')

        if not re.search('[a-zA-Z]', label[0]):  # First letter of a label must be a letter
            log.error(f"Invalid label '{label}': First character of Neo4j :LABEL must be a letter")
        else:
            return f':`{label}`'  # :`LABEL`

    @staticmethod
    def assert_property(prop) -> str:
        prop = f'{prop}'
        prop = prop.strip()

        i = 0
        for char in prop:
            if char == '`':
                i += 1

        if i == 2:
            return prop

        if i < 2:
            prop = prop.replace('`', '')
            prop = f'`{prop}`'

        return prop

    def build_cypher(self, cypher: str):
        """Build cypher line by line"""
        self.cypher += f'{cypher} '
        return self.cypher

    def consolidate(self) -> str:
        """Join cypher queries list into a string"""
        return ' '.join(self.cypher_list).strip()

    def create(self, prop: str, value: str, node: str = None, label: str = ''):
        """Create a node

        CREATE ( node :`label` { `prop`: "value" } )
        """
        n = Node(prop=prop, value=value, node=node, label=label)
        cypher = f'CREATE {n} \n'
        return cypher

    def create_dict(self, prop: str, value: str, data: dict, node: str = None, label: str = ''):
        """Create a node from dict

        CREATE (Node :`human` { `name`: "finn" })
        SET
        Node.first_seen = "2021-02-25T03:19:47.438596+00:00",
        Node.first_seen_ts = timestamp()
        SET
        Node.prop = "value",
        Node.prop = "value"
        SET
        Node.last_seen = "2021-02-25T03:19:47.438901+00:00",
        Node.last_seen_ts = timestamp()
        SET
        Node.prop = "value"
        RETURN *
        """
        cypher = self.create(node=node, label=label, prop=prop, value=value)
        cypher += self.set()
        cypher += self.timestamp_first_seen()

        cypher += self.set()
        cypher += self.dict_to_property(data=data, node=node)

        cypher += self.set()
        cypher += self.timestamp_last_seen(node=node)

        cypher += self.set()
        cypher += self.dict_to_property(data=data, node=node)
        cypher += self.return_all()
        return cypher

    def cypher_end(self):
        """End of cypher"""
        return ') \n'

    def delete_all(self):
        """Delete all nodes and relationships"""
        return 'MATCH (n) DETACH DELETE n'

    def delete_node(self, prop: str, value: str, node: str = None) -> str:
        """Delete all matching nodes and its relationships"""
        # MATCH (n {name: 'Andy'})
        # DETACH DELETE n
        cypher = self.match(prop=prop, value=value, node=node)
        cypher += f'DETACH DELETE {node}'
        return cypher

    def dict_to_property(self, data: dict, node: str = None) -> str:
        """Dict to cypher

        return: node.`key` = "value"
        """

        if not data:
            return f'{{}} \n'

        data = self.prepare_dict(data)
        cypher = []
        i = 1
        for prop in data.keys():
            value = data.get(prop)
            prop = self.assert_property(prop)
            query = self.add_property(node=node, prop=prop, value=value)

            if i < len(data.keys()):
                cypher.append(query + ',\n')
            else:
                cypher.append(query)
            i += 1

        cypher = ''.join(cypher)
        cypher = f'{cypher} \n'
        return cypher

    def match(self, prop: str, value: str, node: str = None, label: str = ''):
        """Match a node

        MATCH (node :label {`prop`: "value"})
        """
        prop = self.assert_property(prop)
        label = self.assert_label(label)

        return f'MATCH ({node} {label} {{ {prop}: "{value}" }}) \n'

    def merge(self, prop: str = None, value: str = None, node: str = None, label: str = ''):
        """Merge a node

        MERGE ( node :`label` { `prop`: "value" } )
        """
        n = Node(prop=prop, value=value, node=node, label=label)
        cypher = f'MERGE {n} \n'
        return cypher

    def merge_dict(self, prop: str, value: str, data: dict, node: str = None, label: str = '') -> str:
        """Merge a node from a dict

        MERGE (Node :`human` { `name`: "finn" })
        ON CREATE
        SET
        Node.first_seen = "2021-02-25T03:19:47.438596+00:00",
        Node.first_seen_ts = timestamp()
        ON CREATE
        SET
        Node.prop = "value",
        Node.prop = "value"
        ON MATCH
        SET
        Node.updated = "2022-01-24T03:41:31.160885+00:00",
        Node.updated_ts = timestamp()
        ON MATCH
        SET
        Node.prop = "value",
        Node.prop = "value"
        RETURN *
        """
        cypher = self.merge(prop=prop, value=value, node=node, label=label)
        cypher += self.on_create()
        cypher += self.timestamp_first_seen()

        cypher += self.on_create()
        cypher += self.dict_to_property(data=data, node=node)

        cypher += self.on_match()
        cypher += self.timestamp_updated()

        cypher += self.on_match()
        cypher += self.dict_to_property(data=data, node=node)
        cypher += self.return_all()
        return cypher

    def on_match(self):
        cypher = 'ON MATCH \n'
        cypher += self.set()
        return cypher

    def on_create(self):
        cypher = 'ON CREATE \n'
        cypher += self.set()
        return cypher

    @staticmethod
    def prepare_dict(blob: dict) -> dict:
        """All inputs first needs to be dicts"""
        try:
            return dict(blob)
        except Exception as _:
            return dict(raw=urlencode(blob))

    def return_all(self):
        """RETURN *"""
        return 'RETURN *'

    def return_node(self, node: str = None):
        """RETURN node"""
        return f'RETURN {node}'

    def relationship(self,
                     A_node: str = 'A', A_label: str = None, A_prop: str = None, A_value: str = None,
                     B_node: str = 'B', B_label: str = None, B_prop: str = None, B_value: str = None,
                     WHERE: str = None, label: str = None, node: str = 'r', direction: str = '->'):
        """Create relationship between two existing nodes

        MATCH (A_node :A_label {`A_prop`: "A_value"})
        MATCH (B_node :B_label {`B_prop`: "B_value"})

        MERGE (a)-[r :label]->(b)
        RETURN *
        """

        A_label = self.assert_label(A_label)
        B_label = self.assert_label(B_label)
        label = self.assert_label(label)

        cypher_a = self.match(node=A_node, label=A_label, prop=A_prop, value=A_value)
        cypher_b = self.match(node=B_node, label=B_label, prop=B_prop, value=B_value)
        cypher_where = f'WHERE {WHERE} \n'
        begin, end = self._relationship_direction(direction)

        cypher = cypher_a
        cypher += cypher_b
        if cypher_where:
            cypher += cypher_where
        cypher += f'MERGE ({A_node}) {begin} [{node} {label}] {end} ({B_node}) \n'
        cypher += self.return_all()

        return cypher

    def _relationship_direction(self, direction: str = '->'):
        """Sets direction of node relationship

        -> or > or >>
        <- or < or <<
        <-> or <>
        """

        begin = '-'
        end = '->'

        if direction == '->' or direction == '>' or direction == '>>':
            begin = '-'
            end = '->'

        if direction == '<-' or direction == '<' or direction == '<<':
            begin = '<-'
            end = '-'

        if direction == '<->' or direction == '<>' or direction == '<<>>':
            begin = '<-'
            end = '->'

        return begin, end

    def unique(self, node: str = None, label: str = ''):
        label = self.assert_label(label)
        return f'UNIQUE ({node} {label} {{'

    def updated(self, node: str = None):
        """Node last_seen property"""
        node = node
        time = datetime.now(tz=timezone.utc).isoformat()
        self.cypher_list.append(f'SET {node}.last_seen = "{time}"')
        self.cypher_list.append(f'SET {node}.last_seen_ts = timestamp()')

    @staticmethod
    def set():
        return 'SET \n'

    def timestamp_first_seen(self, node: str = None) -> str:
        """Node first_seen property

        Node.first_seen = "2022-01-24T03:41:31.160885+00:00",
        Node.first_seen_ts = timestamp()
        """
        time = datetime.now(tz=timezone.utc).isoformat()

        cypher = f'{node}.first_seen = "{time}", \n'
        cypher += f'{node}.first_seen_ts = timestamp() \n'
        return cypher

    def timestamp_last_seen(self, node: str = None) -> str:
        """Node last_seen property

        Node.last_seen = "2022-01-24T03:41:31.160885+00:00",
        Node.last_seen_ts = timestamp()
        """
        time = datetime.now(tz=timezone.utc).isoformat()
        cypher = f'{node}.last_seen = "{time}", \n'
        cypher += f'{node}.last_seen_ts = timestamp() \n'
        return cypher

    def timestamp_updated(self, node: str = None) -> str:
        """Node updated property

        Node.updated = "2022-01-24T03:41:31.160885+00:00",
        Node.updated_ts = timestamp()
        """
        time = datetime.now(tz=timezone.utc).isoformat()
        cypher = f'{node}.updated = "{time}", \n'
        cypher += f'{node}.updated_ts = timestamp() \n'
        return cypher
