import unittest

from automon.integrations.phantom import PhantomClient

c = PhantomClient()


class TestPhantomClient(unittest.TestCase):

    def test_isConnected(self):
        if c.isConnected():
            self.assertTrue(c.isConnected())
        else:
            self.assertFalse(c.isConnected())

    def test_create_artifact(self):
        if c.isConnected():
            self.assertTrue(c.create_artifact(container_id=0))
        else:
            self.assertFalse(c.create_artifact(container_id=0))

    def test_create_container(self):

        if c.isConnected():
            self.assertTrue(c.create_container(label='testing', name='AAAA'))
        else:
            self.assertFalse(c.create_container(label='testing', name='AAAA'))

    def test_delete_containers(self):
        container = 0

        if c.isConnected():
            self.assertTrue(c.delete_container(container_id=container))
        else:
            self.assertFalse(c.delete_container(container_id=container))

    def test_list_aritfacts(self):
        if c.isConnected():
            self.assertTrue(c.list_artifact())

    def test_list_containers(self):
        if c.isConnected():
            self.assertTrue(c.list_containers())
        else:
            self.assertFalse(c.list_containers())


if __name__ == '__main__':
    unittest.main()
