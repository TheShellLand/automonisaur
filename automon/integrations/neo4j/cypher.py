import re

from urllib.parse import urlencode
from datetime import datetime, timezone

from automon.log.logger import Logging

log = Logging(__name__, Logging.DEBUG)


class Cypher:

    def __init__(self):
        self.cypher = []
        self._node = 'Node'

    def start(self, node: str = None, label: str = ''):
        return self.merge(node, label)

    def merge(self, node: str = None, label: str = ''):
        """Default merge node"""
        node = node or self._node
        label = self.assert_label(label)
        self.cypher.append(f'MERGE ({node} {label} {{')

    def create(self, node: str = None, label: str = ''):
        node = node or self._node
        label = self.assert_label(label)
        self.cypher.append(f'CREATE ({node} {label} {{')

    def unique(self, node: str = None, label: str = ''):
        node = node or self._node
        label = self.assert_label(label)
        self.cypher.append(f'UNIQUE ({node} {label} {{')

    def end(self):
        self.cypher.append('})')

    def return_asterisk(self):
        self.cypher.append('RETURN *')

    def timestamp(self, node: str = None):
        node = node or self._node
        time = datetime.now(tz=timezone.utc).isoformat()
        self.cypher.append(f'SET {node}.timestamp = "{time}"')

    def on_create_set(self):
        # timestamp of first seen
        # query.append('ON CREATE SET {}.timestamp = "{}"'.format(node, timestamp_date))
        pass

    # @staticmethod
    # def begin():
    #     return '{'

    def dict_to_cypher(self, obj: dict) -> str:
        """Dict to cypher

        must be { `key`: 'value' }
        """

        obj = self.prepare_dict(obj)
        cypher = []
        i = 1
        for key in obj.keys():
            value = obj.get(key)

            if i < len(obj.keys()):
                cypher.append(f'`{key}`: "{value}",')
            else:
                cypher.append(f'`{key}`: "{value}"')
            i += 1

        self.cypher.append(' '.join(cypher))

    def consolidate(self) -> str:
        """Join cypher queries list into a string"""
        return ' '.join(self.cypher).strip()

    def prepare_dict(self, blob: dict) -> dict:
        """All inputs first needs to dicts"""
        try:
            return dict(blob)
        except Exception as _:
            return dict(raw=urlencode(blob))

    def assert_label(self, label: str) -> str:
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

    @staticmethod
    def delete_all():
        return f'MATCH (n) DELETE n'
