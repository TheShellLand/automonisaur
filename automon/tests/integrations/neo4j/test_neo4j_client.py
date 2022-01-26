import unittest

from automon.integrations.neo4j.client import Neo4jClient
from automon.integrations.neo4j.cypher import Cypher


class Neo4jTest(unittest.TestCase):
    client = Neo4jClient()

    def test_build_cypher(self):
        c = Neo4jClient()
        c.build_cypher('AAAA')
        self.assertTrue(c.cypher)
        self.assertEqual(c.cypher, 'AAAA')

    def test_create_dict(self):

        if self.client.isConnected():
            self.assertTrue(self.client.create_dict(prop='name', value='finn', label='human', data={'powers': 'no'}))
            self.assertTrue(self.client.create_dict(prop='name', value='jake', label='dog', data={'powers': True}))

    def test_merge(self):

        if self.client.isConnected():
            self.assertTrue(self.client.merge(label='dog'))

    def test_merge_dict(self):

        if self.client.isConnected():
            self.assertTrue(self.client.merge_dict(
                prop='name', value='lsp', label='lumpy', data={'powers': 'princess'}))
            self.assertTrue(self.client.merge_dict(
                prop='name', value='bubble gum', label='bubble',
                data={'powers': 'princess', 'specialty': 'science'}))
            self.assertTrue(self.client.merge_dict(
                prop='name', value='BMO', label='gameboy',
                data={'powers': 'buttons', 'specialty': ['green', 'box']}))

    def test_relationships(self):
        if self.client.isConnected():
            self.assertTrue(self.client.merge_dict(
                prop='name', value='lsp', label='lumpy', data={'powers': 'princess'}))
            self.assertTrue(self.client.merge_dict(
                prop='name', value='bubble gum', label='bubble',
                data={'powers': 'princess', 'specialty': 'science'}))
            self.assertTrue(self.client.merge_dict(
                prop='name', value='BMO', label='gameboy',
                data={'powers': 'buttons', 'specialty': ['green', 'box']}))

            self.assertTrue(self.client.relationship(
                A_prop='powers', A_value='princess',
                B_prop='type', B_value='princess', B_label='princess',
                label='is',
                direction='->'
            ))

    def test_delete_node(self):
        if self.client.isConnected():
            self.assertTrue(self.client.merge_dict(
                prop='name', value='Marceline', label='vampire', data={'age': '1000'}))
            self.assertTrue(self.client.delete_match(prop='name', value='Marceline'))

    def test_assert_label(self):
        test = Cypher()

        self.assertEqual(test.assert_label(':test'), ':`test`')
        self.assertIsNone(test.assert_label('1test'))
        self.assertEqual(test.assert_label('works'), ':`works`')


if __name__ == '__main__':
    unittest.main()
