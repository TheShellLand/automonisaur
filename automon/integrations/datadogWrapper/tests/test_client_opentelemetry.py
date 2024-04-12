import asyncio
import unittest

from automon.integrations.datadogWrapper import DatadogOpenTelemetryClient


class MyTestCase(unittest.TestCase):
    client = DatadogOpenTelemetryClient()

    asyncio.run(client.config.instrumentation())

    if asyncio.run(client.is_ready()):
        def test_ready(self):
            self.assertTrue(asyncio.run(
                self.client.is_ready()
            ))

        pass


if __name__ == '__main__':
    unittest.main()
