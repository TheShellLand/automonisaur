import unittest

from automon.integrations.neo4j.client import Neo4jClient


class Neo4jTest(unittest.TestCase):
    client = Neo4jClient()

    def test_cypher(self):
        if self.client.isConnected():
            c = Neo4jClient()

            # self.assertTrue(c.delete_all())
            self.assertTrue(c.create(prop='AAAA', value='BBBB'))
            self.assertTrue(c.cypher_run(f'MATCH (N) RETURN N'))
            self.assertTrue(c.merge(prop='AAAA', value='CCCC'))

            c.build_cypher(f'MATCH (N)')
            c.build_cypher(f'RETURN N')


if __name__ == '__main__':
    unittest.main()
