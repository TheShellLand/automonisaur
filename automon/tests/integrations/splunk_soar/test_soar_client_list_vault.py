import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):
    if c.isConnected():
        def test_list_vault_generator(self):
            test = [x for x in c.list_vault_generator(page_size=1, max_pages=1)]
            if test:
                self.assertTrue(test)


if __name__ == '__main__':
    unittest.main()
