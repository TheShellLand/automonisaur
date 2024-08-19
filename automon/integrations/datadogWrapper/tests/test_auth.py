import asyncio
import unittest

from automon.integrations.datadogWrapper import DatadogClientRest


class MyTestCase(unittest.TestCase):
    client = DatadogClientRest()

    if asyncio.run(client.is_ready()):
        def test_auth(self):
            self.assertTrue(asyncio.run(
                self.client.validate()
            ))

        pass


if __name__ == '__main__':
    unittest.main()
