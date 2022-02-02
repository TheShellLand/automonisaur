import unittest

from automon.integrations.phantom import PhantomClient


class TestPhantomClient(unittest.TestCase):
    c = PhantomClient()

    def test_isConnected(self):
        if self.c.isConnected():
            self.assertTrue(self.c.isConnected())
        else:
            self.assertFalse(self.c.isConnected())

    def test_listContainers(self):
        if self.c.isConnected():
            self.assertTrue(self.c.list_containers())
        else:
            self.assertFalse(self.c.list_containers())


if __name__ == '__main__':
    unittest.main()
