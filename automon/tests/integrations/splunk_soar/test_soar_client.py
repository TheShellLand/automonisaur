import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):
    if c.isConnected():
        def test_isConnected(self):
            self.assertTrue(c.isConnected())

        def test_create_artifact(self):
            id = c.create_container(label='testing', name='testing').id
            self.assertTrue(c.create_artifact(container_id=id))

        def test_create_container(self):
            self.assertTrue(c.create_container(label='testing', name='testing'))

        def test_delete_containers(self):
            container = c.create_container(label='testing', name='testing')
            self.assertTrue(c.delete_container(container_id=container.id))

        def test_get_container(self):
            container = c.create_container(label='testing', name='testing')
            self.assertTrue(c.get_container(container_id=container.id))

        def test_list_artifact(self):
            self.assertTrue(c.list_artifact())

        def test_list_containers(self):
            self.assertTrue(c.list_containers())

        def test_list_vault(self):
            self.assertTrue(c.list_vault())

        def test_get_vault(self):
            container = c.create_container(label='testing', name='testing')

            list_vault = c.list_vault()
            vault = list_vault.get_one()
            if vault:
                self.assertTrue(c.get_vault(vault_id=vault.id))


if __name__ == '__main__':
    unittest.main()
