import unittest

from automon.integrations.neo4j.config import Neo4jConfig


class ConfigTest(unittest.TestCase):
    c = Neo4jConfig()

    def test_config(self):
        self.assertTrue(Neo4jConfig)

    def test_NEO4J_USER(self):
        self.assertEqual(type(self.c.NEO4J_USER), str)

    def test_NEO4J_PASSWORD(self):
        self.assertEqual(type(self.c.NEO4J_PASSWORD), str)

    def test_NEO4J_SERVERS(self):
        self.assertEqual(type(self.c.NEO4J_HOST), str)


if __name__ == '__main__':
    unittest.main()
