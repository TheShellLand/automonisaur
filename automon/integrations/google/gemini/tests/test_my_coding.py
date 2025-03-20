import unittest
import os

from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO
from automon.integrations.google.gemini import GoogleGeminiClient

LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.requestsWrapper.client').setLevel(CRITICAL)
LoggingClient.logging.getLogger('automon.integrations.google.oauth.config').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gemini.config').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(INFO)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)


class TestGoogleGeminiClient(unittest.TestCase):
    def test_client(self):
        gemini = GoogleGeminiClient()

        if gemini.is_ready():

            root = '../automonisaur/automon'

            code = ''
            for path, folders, files in os.walk(root):
                for file in files:
                    full_path = os.path.join(root, path, file)
                    with open(full_path, 'r') as f:
                        try:
                            code += f.read()
                        except:
                            pass

            code = code[:round(1000000)]

            gemini.add_content(role='model', prompt=f"You are to a programmer.")
            gemini.add_content(role='model', prompt=f"You wrote the provided code.")
            gemini.add_content(role='model', prompt=f'<CODE>{code}</CODE>')

            gemini.chat_forever()

            pass


if __name__ == '__main__':
    unittest.main()
