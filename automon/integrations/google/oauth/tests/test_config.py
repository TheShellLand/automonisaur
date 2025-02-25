import unittest

from automon.integrations.google.oauth import GoogleAuthConfig


class MyTestCase(unittest.TestCase):
    def test_config(self):
        test = GoogleAuthConfig()

        if test.is_ready():
            test.Credentials()
            test.userinfo()
            test.refresh_token()

        pass


if __name__ == '__main__':
    unittest.main()
