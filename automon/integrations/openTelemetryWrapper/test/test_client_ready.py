import unittest
import asyncio

from automon.integrations.openTelemetryWrapper import OpenTelemetryClient


class MyTestCase(unittest.TestCase):
    client = OpenTelemetryClient()

    def test_client(self):
        self.assertTrue(asyncio.run(
            self.client.is_ready()
        ))


if __name__ == '__main__':
    unittest.main()
