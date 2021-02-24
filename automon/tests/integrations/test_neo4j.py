import json
import unittest

from automon.integrations.neo4j.client import Neo4jClient


class Neo4jTest(unittest.TestCase):
    client = Neo4jClient()

    def test_Neo4jClient(self):
        self.assertIsNotNone(Neo4jClient())

    def test_send_data(self):
        if self.client.connected:
            self.assertTrue(self.client.send_data('human', {'name': 'eric'}))


if __name__ == '__main__':
    unittest.main()
