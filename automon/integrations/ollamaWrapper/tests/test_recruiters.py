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

        RAG = open('RAG.txt', 'r').read()
        RESUME = open('RESUME.txt', 'r').read()

        model.add_chain(
            f"You are a user talking to a tech recruiter. "
            f"USER: The user provides a resume: {RESUME}. \n\n"
            f"RECRUITER: The recruiter provides a job: {RAG}, \n\n"
            f"Fully and thoroughly analyze the user's resume and imagine the efforts taken to learn and collect "
            f"all of the user's experience and knowledge. Then, write a full report on the relevance the user's resume "
            f"has with the job description, including the percent the resume is relevant."
        ).chat().add_chain(
            f"Write a summary in the first person, in yaml format that must answer all of the following questions: \n"
            f"- What is the percent relevance? \n"
            f"- What are the reasons the resume is relevant to the job? \n "
            f"- Would you apply to this job? \n"
            f"\n"
            f"Use the following: \n"
        ).chat()


if __name__ == '__main__':
    unittest.main()
