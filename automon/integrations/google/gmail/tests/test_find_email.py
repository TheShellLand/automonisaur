import unittest

from automon.integrations.google.gmail import GoogleGmailClient
from automon import LoggingClient, ERROR, DEBUG

LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        gmail = GoogleGmailClient()
        # client.config.add_gmail_scopes()
        gmail.config.add_scopes(
            ["https://mail.google.com/"]
        )

        if gmail.is_ready():
            gmail.config.Credentials()
            gmail.config.userinfo()
            gmail.config.build_service()
            gmail.labels_list()
            gmail.draft_list()
            d = gmail.draft_list_automon()
            gmail.users_getProfile()
            # client.history_list(startHistoryId='73211814')
            gmail.messages_list()
            msg = gmail.messages_get('1953dbd795081667', format=gmail.v1.Format.full)

        pass


if __name__ == '__main__':
    unittest.main()
