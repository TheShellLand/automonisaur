import json
import unittest

from automon.integrations.neo4j.client import Neo4jClient


class Neo4jTest(unittest.TestCase):

    def test_Neo4jWrapper(self):
        self.assertTrue(Neo4jClient())


if __name__ == '__main__':
    unittest.main()
