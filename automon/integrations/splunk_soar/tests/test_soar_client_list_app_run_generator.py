import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):
    if c.is_connected():
        def test_list_app_run_generator(self):
            self.assertTrue([x for x in c.list_app_run_generator(page_size=1)])


if __name__ == '__main__':
    unittest.main()
