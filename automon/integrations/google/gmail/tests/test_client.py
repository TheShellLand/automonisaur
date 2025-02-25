import unittest

from automon.integrations.google.gmail import GoogleGmailClient, GoogleGmailConfig


class MyTestCase(unittest.TestCase):
    def test_something(self):
        client = GoogleGmailClient()
        # client.config.add_scopes(
        #     ['https://www.googleapis.com/auth/gmail.labels']
        # )
        client.config.add_gmail_scopes()

        if client.is_ready():
            client.config.Credentials()
            client.config.userinfo()
            client.config.build_service()
            client.labels_list()
            client.draft_list()
            client.users_getProfile()
            # client.history_list(startHistoryId='73211814')

        pass


if __name__ == '__main__':
    unittest.main()
