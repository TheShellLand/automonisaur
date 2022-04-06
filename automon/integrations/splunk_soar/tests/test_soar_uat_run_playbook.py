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

    def test_cancel_playbook(self):
        if c.isConnected():
            container = c.create_container(label='testing', name='testing')
            playbook = ''

            if playbook:
                run = c.run_playbook(
                    container_id=container.id,
                    playbook_id=playbook
                )
                get = c.get_playbook_run(playbook_run_id=run.playbook_run_id)
                cancel = c.cancel_playbook_run(run.playbook_run_id)


if __name__ == '__main__':
    unittest.main()
