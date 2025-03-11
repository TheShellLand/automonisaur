import unittest

from automon.integrations.google.gemini import GoogleGeminiClient


class TestGoogleGeminiClient(unittest.TestCase):
    def test_client(self):
        gemini = GoogleGeminiClient()

        if gemini.is_ready():
            gemini.add_content("what is today's date?").chat()

            pass


if __name__ == '__main__':
    unittest.main()
