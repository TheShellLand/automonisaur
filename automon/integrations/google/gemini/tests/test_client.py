import unittest

from automon.integrations.google.gemini import GoogleGeminiClient


class TestGoogleGeminiClient(unittest.TestCase):
    def test_client(self):
        test = GoogleGeminiClient()

        if test.is_ready():
            test.add_content("what is today's date?").chat()

            pass


if __name__ == '__main__':
    unittest.main()
