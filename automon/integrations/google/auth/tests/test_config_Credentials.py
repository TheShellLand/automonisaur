import unittest

from automon.integrations.google.auth import GoogleAuthConfig


class MyTestCase(unittest.TestCase):
    def test_something(self):
        test = GoogleAuthConfig()
        if test.Credentials:
            self.assertTrue(test.Credentials)


if __name__ == '__main__':
    unittest.main()
