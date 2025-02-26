import unittest
import json

from automon.integrations.ollamaWrapper import OllamaClient
from automon.helpers.osWrapper import environ

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, ERROR

LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)


class TestOllamaClient(unittest.TestCase):
    def test_chat(self):
        model = OllamaClient()
        model.STREAM = True

        if not model.is_ready() or not environ('RUN'):
            return

        RAG = open('RAG.txt', 'r').read()

        model.add_chain(
            f"""
            You are a chatbot agent answering customer's questions in a chat.
            Your task is to answer questions using data provided in the <DATA> section.
            
            <DATA>
            <RAW>
            {RAG}
            </RAW>
            </DATA>
            
            <INSTRUCTIONS>
            -   Always give a truthful and honest percentage of relevance of the resume to the job.
            -   You are allowed to ask a follow up question if it will help clarify.
            -   For everything else, please explicitly mention these notes. 
            -   Answer in plain English and no sources are required.
            -   Chat with the customer so far is under the <CHAT> section.
            -   Provide answer inside <ANSWER> tags. 
            </INSTRUCTIONS>
            
            
            QUESTION: Give me 10 pokemon nicknames that are related to the color grey. 
            ANSWER:
            
            """
        ).chat().add_chain(
            f"""
            QUESTION: Give me a creative summary of the chat.
            """
        ).chat()


if __name__ == '__main__':
    unittest.main()
