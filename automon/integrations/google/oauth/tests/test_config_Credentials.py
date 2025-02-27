import unittest

from automon.integrations.google.oauth import GoogleAuthConfig


class MyTestCase(unittest.TestCase):
    def test_something(self):
        test = GoogleAuthConfig()
        if test.is_ready():
            self.assertTrue(test.Credentials())


if __name__ == '__main__':
    unittest.main()
