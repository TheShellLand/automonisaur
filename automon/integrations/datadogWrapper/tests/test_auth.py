import unittest

from automon.integrations.datadogWrapper import DatadogClientRest


class MyTestCase(unittest.TestCase):
    client = DatadogClientRest()

    if client.is_ready():
        def test_auth(self):
            self.assertTrue(
                self.client.validate()
            )

        pass


if __name__ == '__main__':
    unittest.main()
