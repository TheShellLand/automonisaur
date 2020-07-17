import json
import unittest

from automon.integrations.neo4j import Neo4jWrapper


class Neo4jTest(unittest.TestCase):

    def test_Neo4jWrapper(self):
        self.assertTrue(Neo4jWrapper)
        self.assertTrue(Neo4jWrapper())

# if __name__ == '__main__':
#     unittest.main()
