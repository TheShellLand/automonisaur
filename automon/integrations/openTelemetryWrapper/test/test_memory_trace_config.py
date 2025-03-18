import unittest

from automon.integrations.openTelemetryWrapper import OpenTelemetryConfig


class MyTestCase(unittest.TestCase):
    config = OpenTelemetryConfig()

    def test_something(self):

        if self.config.is_ready():
            self.assertTrue(
                self.config.test()
            )


if __name__ == '__main__':
    unittest.main()
