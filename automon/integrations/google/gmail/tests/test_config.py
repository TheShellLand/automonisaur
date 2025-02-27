import unittest

from automon.integrations.google.gmail import GoogleGmailConfig


class MyTestCase(unittest.TestCase):
    def test_something(self):
        conf = GoogleGmailConfig()
        conf.add_scopes(
            ['https://www.googleapis.com/auth/gmail.labels']
        )

        if conf.is_ready():
            conf.Credentials()
            conf.userinfo()
            conf.refresh_token()
            conf.build_service()

        pass


if __name__ == '__main__':
    unittest.main()
