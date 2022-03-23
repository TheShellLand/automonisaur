import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):

    def test_run_playbook(self):
        if c.isConnected():
            container = c.create_container(label='testing', name='testing')
            playbook = ''
            c.run_playbook(
                container_id=container.id,
                playbook_id=playbook
            )


if __name__ == '__main__':
    unittest.main()
