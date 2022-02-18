import unittest

from automon.integrations.google import PeopleClient
from automon.integrations.neo4j import Neo4jClient

c = PeopleClient()
n = Neo4jClient()


class TestClient(unittest.TestCase):

    def test_create_nodes(self):
        if c.isConnected():
            contacts = c.list_connections().contacts
            for contact in contacts:
                n.merge_dict(contact)
            pass


if __name__ == '__main__':
    unittest.main()
