import unittest

from automon.integrations.google.auth import AuthConfig


class MyTestCase(unittest.TestCase):
    def test_something(self):
        test = AuthConfig()
        if test.Credentials:
            self.assertTrue(test.Credentials)


if __name__ == '__main__':
    unittest.main()
