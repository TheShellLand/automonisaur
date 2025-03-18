import unittest

from automon.integrations.openTelemetryWrapper import OpenTelemetryClient


class MyTestCase(unittest.TestCase):
    client = OpenTelemetryClient()

    def test_client(self):
        if self.client.is_ready():
            self.assertTrue(
                self.client.is_ready()
            )


if __name__ == '__main__':
    unittest.main()
