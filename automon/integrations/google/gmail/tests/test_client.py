import unittest

from automon.integrations.google.gmail import GoogleGmailClient, GoogleGmailConfig, Format


class MyTestCase(unittest.TestCase):
    def test_something(self):
        client = GoogleGmailClient()
        # client.config.add_gmail_scopes()
        client.config.add_scopes(
            ["https://mail.google.com/"]
        )

        if client.is_ready():
            client.config.Credentials()
            client.config.userinfo()
            client.config.build_service()
            client.labels_list()
            client.draft_list()
            client.users_getProfile()
            # client.history_list(startHistoryId='73211814')
            client.messages_list()
            client.messages_get('1953dbd795081667', format=Format.raw)

        pass


if __name__ == '__main__':
    unittest.main()
