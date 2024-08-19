import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class MyTestCase(unittest.TestCase):
    def test_get_action_run(self):
        if c.is_connected():
            action_run = c.get_action_run(action_run_id=3040610)
            if action_run.id:
                self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
