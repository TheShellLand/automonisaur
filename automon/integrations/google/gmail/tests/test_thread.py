import unittest

from automon.integrations.google.gmail import GoogleGmailClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO

LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.requestsWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.google.oauth.config').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gemini.config').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)

gmail = GoogleGmailClient()

# gmail.config.add_gmail_scopes()
gmail.config.add_scopes(
    ["https://mail.google.com/"]
)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        if not gmail.is_ready():
            return

        gmail.thread_list(maxResults=1)
        gmail.thread_list_automon(maxResults=1)
        # gmail.thread_get()
        # gmail.thread_delete()
        # gmail.thread_trash()
        # gmail.thread_untrash()

        pass


if __name__ == '__main__':
    unittest.main()
