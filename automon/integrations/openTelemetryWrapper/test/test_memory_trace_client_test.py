import unittest
import asyncio

from automon.integrations.openTelemetryWrapper import OpenTelemetryClient


class MyTestCase(unittest.TestCase):
    client = OpenTelemetryClient()

    def test_something(self):
        self.assertTrue(asyncio.run(
            self.client.test()))

        # spans = asyncio.run(
        #     self.client.get_finished_spans())

        pass


if __name__ == '__main__':
    unittest.main()
