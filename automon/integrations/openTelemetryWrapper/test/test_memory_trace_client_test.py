import unittest

from automon.integrations.openTelemetryWrapper import OpenTelemetryClient


class MyTestCase(unittest.TestCase):
    client = OpenTelemetryClient()

    def test_something(self):
        self.assertTrue(self.client.test())

        # spans = 
        #     self.client.get_finished_spans(

        pass


if __name__ == '__main__':
    unittest.main()
