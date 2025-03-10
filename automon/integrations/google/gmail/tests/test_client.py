import unittest

from automon.integrations.google.gmail import GoogleGmailClient
from automon import LoggingClient, ERROR, DEBUG
from automon.integrations.ollamaWrapper import OllamaClient

LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        gmail = GoogleGmailClient()
        # gmail.config.add_gmail_scopes()
        gmail.config.add_scopes(
            ["https://mail.google.com/"]
        )

        if gmail.is_ready():
            q = None
            email_search = gmail.messages_list_automon(
                q=q,
                maxResults=3,
            )

            gmail.messages_get_automon(id='19566a35f24f7b42')

        pass


if __name__ == '__main__':
    unittest.main()
