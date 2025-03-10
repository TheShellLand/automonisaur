import unittest

from automon.integrations.ollamaWrapper import OllamaClient
from automon.helpers.osWrapper import environ


class TestOllamaClient(unittest.TestCase):
    def test_chat(self):
        ollama = OllamaClient()

        if not ollama.is_ready():
            return

        ollama.list()
        ollama.set_model('deepseek-r1:8b')

        pass


if __name__ == '__main__':
    unittest.main()
