import unittest
import os

from automon.integrations.ollamaWrapper import OllamaClient
from automon.helpers.osWrapper import environ

from automon.helpers.loggingWrapper import LoggingClient

LoggingClient.logging.getLogger('httpx').setLevel(LoggingClient.ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(LoggingClient.ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(LoggingClient.ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(LoggingClient.CRITICAL)


class TestOllamaClient(unittest.TestCase):
    def test_chat(self):
        model = OllamaClient()
        model.STREAM = True

        if not model.is_ready() or not environ('RUN'):
            return

        model.add_chain(
            "What are the key features of the XSOAR platform?"
        ).chat().print_response().add_chain(
            "Create a paragraph, in first person, as if you are writing a resume, "
            "that has a few details on how you used XSOAR to solve large automation problems. "
            "Give a response that is less than 10% chance of being written by ChatGPT. "
            "And display the percentage of it written by ChatGPT. "
            "Use the following information: "
        ).chat().print_response()


if __name__ == '__main__':
    unittest.main()
