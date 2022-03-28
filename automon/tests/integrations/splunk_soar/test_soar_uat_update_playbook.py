import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):

    def test_update_playbook(self):
        if c.isConnected():
            container = c.create_container(label='testing', name='testing')
            playbook = ''

            if playbook:
                run = c.run_playbook(container_id=container.id, playbook_id=playbook)
                get_run = c.get_playbook_run(playbook_run_id=run.playbook_run_id)
                c.update_playbook(
                    playbook_id=get_run.playbook,
                    active=False
                )


if __name__ == '__main__':
    unittest.main()
