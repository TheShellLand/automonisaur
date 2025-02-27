import unittest

from automon.integrations.google.oauth import GoogleAuthClient


class MyTestCase(unittest.TestCase):
    def test_authenticate(self):
        test = GoogleAuthClient()
        # scopes = ['https://www.googleapis.com/auth/contacts.readonly']
        # client = AuthClient(serviceName='people', scopes=scopes)
        if test.is_ready():
            self.assertTrue(test.authenticate())


if __name__ == '__main__':
    unittest.main()
