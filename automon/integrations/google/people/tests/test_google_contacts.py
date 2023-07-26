import unittest

from automon.integrations.google import PeopleClient

c = PeopleClient()


class TestClient(unittest.TestCase):
    def test_list_connections(self):
        if c.isConnected():
            self.assertTrue(list(c.list_connection_generator()))


if __name__ == '__main__':
    unittest.main()
