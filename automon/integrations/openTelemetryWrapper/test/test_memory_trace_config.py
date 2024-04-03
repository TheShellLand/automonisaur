import unittest
import asyncio

from automon.integrations.openTelemetryWrapper import OpenTelemetryConfig


class MyTestCase(unittest.TestCase):
    config = OpenTelemetryConfig()

    def test_something(self):
        self.assertTrue(asyncio.run(
            self.config.test())
        )


if __name__ == '__main__':
    unittest.main()
