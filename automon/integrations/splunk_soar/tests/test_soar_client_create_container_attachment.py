import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):
    if c.is_connected():
        def test_soar_client_create_container_attachment(self):
            container = c.create_container(label='testing', name='testing')
            container = c.get_container(container_id=container.id)

            from .dino import dino
            attachment = c.create_container_attachment(
                container_id=container.id,
                file_name='dino.png',
                file_content=dino,
                metadata=None
            )

            self.assertTrue(attachment.vault_id)


if __name__ == '__main__':
    unittest.main()
