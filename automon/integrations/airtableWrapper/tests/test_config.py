import unittest

from automon.integrations.airtableWrapper import AirtableConfig


class MyTestCase(unittest.TestCase):
    def test_something(self):
        test = AirtableConfig()
        if test.is_ready():
            self.assertTrue(test.headers())


if __name__ == '__main__':
    unittest.main()
