import unittest

from automon.integrations.phantom import PhantomClient


class TestPhantomClient(unittest.TestCase):
    c = PhantomClient()

    def test_isConnected(self):
        self.assertTrue(self.c.isConnected())

    def test_listContainers(self):
        self.assertTrue(self.c.list_containers())


if __name__ == '__main__':
    unittest.main()
