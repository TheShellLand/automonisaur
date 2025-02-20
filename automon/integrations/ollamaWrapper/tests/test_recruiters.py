import unittest

from automon.integrations.ollamaWrapper import OllamaClient
from automon.helpers.osWrapper import environ

from automon.helpers.loggingWrapper import LoggingClient

LoggingClient.logging.getLogger('httpx').setLevel(LoggingClient.ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(LoggingClient.ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(LoggingClient.DEBUG)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(LoggingClient.ERROR)


class TestOllamaClient(unittest.TestCase):
    def test_chat(self):
        model = OllamaClient()
        model.STREAM = True

        if not model.is_ready() or not environ('RUN'):
            return

        RAG = open('RAG.txt', 'r').read()
        RESUME = open('RESUME.txt', 'r').read()

        model.add_chain(
            "Give me the percentage the resume is relative to the job description\n"
            f"<job description>{RAG}</job description>"
            f"<resume>{RESUME}</resume>"
        ).chat().print_response()


if __name__ == '__main__':
    unittest.main()
