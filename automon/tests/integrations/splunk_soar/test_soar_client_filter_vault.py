import unittest

from automon.integrations.splunk_soar import SplunkSoarClient

c = SplunkSoarClient()


class TestClient(unittest.TestCase):
    if c.isConnected():
        def test_list_vault_generator(self):
            filter = 'ca3f4b65155db20d6e1d3b5fee8ef8bf0d968548'
            test = c.filter_vault(filter=filter, page_size=200)
            if test:
                self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
