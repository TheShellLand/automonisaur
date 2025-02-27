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
        RESUME = open('RESUME.txt', 'r').read()

        model.add_chain(
            f"""
            You are a highly articulate chat bot. 
            
            Your task is to answer questions using data provided in the <DATA> section.
            
                - Your resume is in the <RESUME> section. 
                - The job description is in the <JOB> section.
            
            
            <DATA>
            <RESUME>
            {RESUME}
            </RESUME>
            
            <JOB>
            {RAG}
            </JOB>
            </DATA>
            
            <INSTRUCTIONS>
            -   Always give a truthful and honest percentage of relevance of the resume to the job.
            -   After providing truthful and honest answer, follow up with a following section that will construct
                an answer that will be the most likely to land the job.
            -   You are allowed to ask a follow up question if it will help clarify experience from the resume.
            -   You can only answer questions related to your resume and job description. Include the resume job and 
                experience in the response, when applicable.
            -   For everything else, please explicitly mention these notes. 
            -   Answer in plain English and no sources are required
            -   Chat with the customer so far is under the CHAT section.
            </INSTRUCTIONS>
            
            
            QUESTION: In a summary, how relevant is your resume is with the job? (include a percentage in the summary)
            ANSWER:
            
            """
        ).chat()


if __name__ == '__main__':
    unittest.main()
