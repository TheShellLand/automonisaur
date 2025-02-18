import unittest
import os

from automon.integrations.ollamaWrapper import OllamaClient
from automon.helpers.osWrapper import environ


from automon.helpers.loggingWrapper import LoggingClient

LoggingClient.logging.getLogger('httpx').setLevel(LoggingClient.ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(LoggingClient.ERROR)
# LoggingClient.logging.getLogger('httpcore.http11').setLevel(LoggingClient.ERROR)
# LoggingClient.logging.getLogger('httpcore.connection').setLevel(LoggingClient.ERROR)


class TestOllamaClient(unittest.TestCase):
    def test_chat(self):
        model = OllamaClient()
        model.STREAM = True

        if not model.is_ready() or not environ('RUN'):
            return

        RAG = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RAG.txt'), 'r').read()
        QUERY = input('Enter your question: ')

        model.add_message(content=f'You are a USER and a ASSISTANT.')

        model.add_message(content=f'As the ASSISTANT, you provided the following information to USER: {RAG}')
        model.add_message(content=f"As the USER, do the following: {QUERY}")

        model.add_message(content=f'As the USER, your replies are in informal tone.')

        model.chat()
        model.print_response()


if __name__ == '__main__':
    unittest.main()
