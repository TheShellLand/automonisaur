import unittest

from automon.integrations.phantom import PhantomClient

c = PhantomClient()


class TestPhantomClient(unittest.TestCase):

    def test_isConnected(self):
        if c.isConnected():
            self.assertTrue(c.isConnected())
        else:
            self.assertFalse(c.isConnected())

    def test_list_containers(self):
        if c.isConnected():
            self.assertTrue(c.list_containers())
        else:
            self.assertFalse(c.list_containers())

    def test_delete_containers(self):
        container = 0

        if c.isConnected():
            self.assertTrue(c.delete_containers(identifier=container))
        else:
            self.assertFalse(c.delete_containers(identifier=container))

    def test_create_container(self):

        if c.isConnected():
            self.assertTrue(c.create_container(label='testing', name='AAAA'))
        else:
            self.assertFalse(c.create_container(label='testing', name='AAAA'))


if __name__ == '__main__':
    unittest.main()
