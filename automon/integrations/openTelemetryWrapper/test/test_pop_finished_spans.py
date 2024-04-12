import unittest
import asyncio

from automon.integrations.openTelemetryWrapper import OpenTelemetryConfig


class MyTestCase(unittest.TestCase):
    config = OpenTelemetryConfig()

    if asyncio.run(config.is_ready()):
        test = asyncio.run(config.test())

        def test_pop_finished_spans(self):
            spans = asyncio.run(self.config.pop_finished_spans())
            self.assertIsNotNone(spans)

            pass

    pass


if __name__ == '__main__':
    unittest.main()
