import unittest

from automon.integrations.openTelemetryWrapper import OpenTelemetryConfig


class MyTestCase(unittest.TestCase):
    config = OpenTelemetryConfig()

    if config.is_ready():
        test = config.test()

        def test_pop_finished_spans(self):
            spans = self.config.pop_finished_spans()
            self.assertIsNotNone(spans)

            pass

    pass


if __name__ == '__main__':
    unittest.main()
