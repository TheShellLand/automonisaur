import unittest

from automon.integrations.ollamaWrapper import OllamaClient
from automon.helpers.osWrapper import environ

from automon.helpers.loggingWrapper import LoggingClient

LoggingClient.logging.getLogger('httpx').setLevel(LoggingClient.ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(LoggingClient.ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(LoggingClient.DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(LoggingClient.ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(LoggingClient.ERROR)


class TestOllamaClient(unittest.TestCase):
    def test_chat(self):
        model = OllamaClient()
        model.STREAM = True

        if not model.is_ready() or not environ('RUN'):
            return

        model.add_chain(
            f"Is Logical thinking a subset of Critical thinking or vice versa?"
        ).chat()


if __name__ == '__main__':
    unittest.main()
