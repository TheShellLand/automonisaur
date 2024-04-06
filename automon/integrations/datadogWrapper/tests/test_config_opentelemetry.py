import asyncio
import unittest

from automon.integrations.datadogWrapper import DatadogOpenTelemetryConfig


class MyTestCase(unittest.TestCase):
    test = DatadogOpenTelemetryConfig()

    def test_instrumentation(self):
        self.assertTrue(asyncio.run(
            self.test.instrumentation()
        ))

        pass


if __name__ == '__main__':
    unittest.main()
