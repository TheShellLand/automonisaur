import unittest

from automon.integrations.ollamaWrapper import OllamaClient
from automon.helpers.osWrapper import environ


class TestOllamaClient(unittest.TestCase):
    def test_chat(self):
        model = OllamaClient()

        if not model.is_ready() and not environ('RUN'):
            return

        model.pull()

        model.add_message(
            "What time is it?"
        )
        model.chat()

        model.print_response()


if __name__ == '__main__':
    unittest.main()
