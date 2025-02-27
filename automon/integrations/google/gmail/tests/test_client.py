import unittest

from automon.integrations.google.gmail import GoogleGmailClient, GoogleGmailConfig, Format
from automon import LoggingClient, ERROR, DEBUG


LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)


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
            msg = client.messages_get('1953dbd795081667', format=Format.full).payload_decoded

            from automon.integrations.ollamaWrapper import OllamaClient

            OllamaClient().use_template_chatbot_with_input(input=msg, question="Parse all url addresses.").chat()

        pass


if __name__ == '__main__':
    unittest.main()
