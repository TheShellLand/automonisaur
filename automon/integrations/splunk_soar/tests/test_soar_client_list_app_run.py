import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):
    if c.is_connected():
        def test_list_app_run(self):
            self.assertTrue(c.list_app_run(page_size=1))


if __name__ == '__main__':
    unittest.main()
