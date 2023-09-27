import unittest

from automon.integrations.google.people import GooglePeopleClient

c = GooglePeopleClient()


class TestClient(unittest.TestCase):
    def test_list_connections(self):
        if c.isConnected():
            self.assertTrue(list(c.list_connection_generator()))


if __name__ == '__main__':
    unittest.main()
