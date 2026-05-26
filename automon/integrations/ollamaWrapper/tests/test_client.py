import unittest

from automon.integrations.ollamaWrapper import OllamaClient
from automon.helpers.osWrapper import environ


class TestOllamaClient(unittest.TestCase):
    def test_chat(self):
        ollama = OllamaClient()
        model = ollama.model

        if not ollama.is_ready():
            return

        if not ollama.pull_model(model):
            return

        ollama.add_prompt(
            "What time is it?"
        )
        ollama.chat()

        ollama.print_response()

        pass


if __name__ == '__main__':
    unittest.main()
