import unittest

from automon.integrations.google.people import GooglePeopleClient
from automon.integrations.neo4jWrapper import Neo4jClient

c = GooglePeopleClient()
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
