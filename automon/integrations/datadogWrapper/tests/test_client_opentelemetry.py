import asyncio
import unittest

from automon.integrations.datadogWrapper import DatadogOpenTelemetryClient


class MyTestCase(unittest.TestCase):
    client = DatadogOpenTelemetryClient()

    # client.config.instrumentation()

    if client.is_ready():
        def test_ready(self):
            self.assertTrue(
                self.client.is_ready()
            )

        pass


if __name__ == '__main__':
    unittest.main()
