import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):

    def test_isConnected(self):
        if c.isConnected():
            self.assertTrue(c.isConnected())
        else:
            self.assertFalse(c.isConnected())

    def test_create_artifact(self):
        if c.isConnected():
            id = c.create_container(label='testing', name='testing').id
            self.assertTrue(c.create_artifact(container_id=id))
        else:
            self.assertFalse(c.create_artifact(container_id=0))

    def test_create_container(self):
        if c.isConnected():
            self.assertTrue(c.create_container(label='testing', name='testing'))
        else:
            self.assertFalse(c.create_container(label='testing', name='testing'))

    def test_delete_containers(self):
        if c.isConnected():
            id = c.create_container(label='testing', name='testing').id
            self.assertTrue(c.delete_container(container_id=id))
        else:
            self.assertFalse(c.delete_container(container_id=0))

    def test_list_artifact(self):
        if c.isConnected():
            self.assertTrue(c.list_artifact())
        else:
            self.assertFalse(c.list_artifact())

    def test_list_containers(self):
        if c.isConnected():
            self.assertTrue(c.list_containers())
        else:
            self.assertFalse(c.list_containers())


if __name__ == '__main__':
    unittest.main()
