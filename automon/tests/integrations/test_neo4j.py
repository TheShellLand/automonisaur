import json
import unittest

from automon.integrations.neo4j.client import Neo4jClient
from automon.integrations.neo4j.config import Neo4jConfig
from automon.integrations.neo4j.cypher import Cypher


class Neo4jTest(unittest.TestCase):
    client = Neo4jClient(Neo4jConfig(encrypted=False))

    def test_Neo4jClient(self):
        self.assertIsNotNone(Neo4jClient(hosts='bolt://localhost:0', encrypted=False))

    def test_cypher(self):
        if self.client.connected:
            # self.assertTrue(self.client.delete_all())
            self.assertTrue(self.client.merge(label='human', data={'name': 'finn'}))
            self.assertTrue(self.client.merge(label='dog', data={'name': 'jake', 'magic': True}))
            self.assertTrue(self.client.merge(label='dog', data={'name': 'jake'}))
            self.assertTrue(self.client.merge(label='dog', data={'name': 'jake', 'magic': False}))
            self.assertTrue(self.client.merge(label='math', data={'results': 1}))
            self.assertTrue(self.client.merge(label='big dict', data={'isthat': 'new', 'no': "it's not"}))
            self.assertTrue(self.client.merge(data={'no': 'labels', 'look': 'mom'}))
            self.assertTrue(self.client.merge(data={'no': 'labels', 'look': 'mom'}))
            # self.assertTrue(self.client.delete_all())

    def test_relationships(self):
        if self.client.connected:
            pass

    def test_assert_label(self):
        test = Cypher()

        self.assertEqual(test.assert_label(':test'), ':`test`')
        self.assertIsNone(test.assert_label('1test'))
        self.assertEqual(test.assert_label('works'), ':`works`')


if __name__ == '__main__':
    unittest.main()
