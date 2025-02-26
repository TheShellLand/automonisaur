import unittest

from automon.integrations.ollamaWrapper import OllamaClient

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, ERROR, CRITICAL

LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(CRITICAL)


class TestOllamaClient(unittest.TestCase):
    def test_chat(self):
        model = OllamaClient()

        model.chat_forever(system_content=model.use_template_chatbot_with_thinking())


if __name__ == '__main__':
    unittest.main()
