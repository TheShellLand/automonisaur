import unittest

from automon.integrations.neo4j.client import Neo4jClient
from automon.integrations.neo4j.cypher import Cypher


class Neo4jTest(unittest.TestCase):
    client = Neo4jClient()

    def test_cypher(self):

        if self.client.isConnected():
            # self.assertTrue(self.client.delete_all())
            self.assertTrue(self.client.create_node(label='human', data={'name': 'finn', 'friend': 'jake'}))
            self.assertTrue(self.client.create_node(label='human', data={'name': 'finn'}))
            self.assertTrue(self.client.merge_dict(label='human', data={'name': 'finn'}))
            self.assertTrue(self.client.merge_dict(label='dog', data={'name': 'jake', 'magic': True}))
            self.assertTrue(self.client.merge_dict(label='dog', data={'name': 'jake'}))
            self.assertTrue(self.client.merge_dict(label='math', data={'results': 1}))
            self.assertTrue(self.client.merge_dict(label='big dict', data={'isthat': 'new', 'no': "it's not"}))
            self.assertTrue(self.client.merge_dict(data={'no': 'labels', 'look': 'mom'}))
            # self.assertTrue(self.client.delete_all())

    def test_relationships(self):
        if self.client.isConnected():
            self.assertTrue(self.client.merge_dict(label='bubble tea', data={'type': 'milk tea'}))
            self.assertTrue(self.client.merge_dict(label='bubble tea', data={'type': 'earl grey'}))

            self.assertTrue(self.client.create_relationship(
                'bubble tea',
                'type', 'milk tea',
                'type', 'earl grey',
                'better than'))

    def test_delete_node(self):
        if self.client.isConnected():
            self.assertTrue(self.client.create_node(label='orange', data={'type': 'juice'}))
            self.assertTrue(self.client.create_node(label='orange', data={'flavor': 'orange'}))

            self.assertTrue(self.client.delete_match(prop='type', value='juice'))
            self.assertTrue(self.client.delete_match(prop='flavor', value='orange'))

            self.assertTrue(self.client.create_node(label='orange', data={'type': 'juice'}))
            self.assertTrue(self.client.create_node(label='orange', data={'flavor': 'orange'}))

    def test_assert_label(self):
        test = Cypher()

        self.assertEqual(test.assert_label(':test'), ':`test`')
        self.assertIsNone(test.assert_label('1test'))
        self.assertEqual(test.assert_label('works'), ':`works`')


if __name__ == '__main__':
    unittest.main()
