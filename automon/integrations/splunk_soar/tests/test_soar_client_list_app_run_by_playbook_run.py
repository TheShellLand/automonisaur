import unittest
import warnings

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):
    if c.is_connected():
        def test_list_app_run_by_playbook_run(self):
            # TODO: create test list_app_run_by_playbook_run
            pass


if __name__ == '__main__':
    unittest.main()
