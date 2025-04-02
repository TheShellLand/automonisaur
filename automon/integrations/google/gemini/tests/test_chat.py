import unittest

from automon.integrations.google.gemini import GoogleGeminiClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO

LoggingClient.logging.getLogger('automon.integrations.requestsWrapper.client').setLevel(ERROR)


class TestGoogleGeminiClient(unittest.TestCase):
    def test_client(self):
        gemini = GoogleGeminiClient()

        if gemini.is_ready():
            gemini.chat_forever()


if __name__ == '__main__':
    unittest.main()
