import unittest

from automon.integrations.phantom import PhantomClient


class TestPhantomClient(unittest.TestCase):
    c = PhantomClient()

    def test_isConnected(self):
        if self.c.isConnected():
            self.assertTrue(self.c.isConnected())
        else:
            self.assertFalse(self.c.isConnected())

    def test_list_containers(self):
        if self.c.isConnected():
            self.assertTrue(self.c.list_containers())
        else:
            self.assertFalse(self.c.list_containers())

    def test_delete_containers(self):
        container = 0

        if self.c.isConnected():
            self.assertTrue(self.c.delete_containers(identifier=container))
        else:
            self.assertFalse(self.c.delete_containers(identifier=container))

    def test_create_container(self):
        container = {}

        if self.c.isConnected():
            self.assertTrue(self.c.create_container(container))
        else:
            self.assertFalse(self.c.create_container(container))


if __name__ == '__main__':
    unittest.main()
