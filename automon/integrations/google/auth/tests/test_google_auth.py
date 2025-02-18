import unittest

from automon.integrations.google.auth import GoogleAuthClient


class MyTestCase(unittest.TestCase):
    def test_authenticate(self):
        test = GoogleAuthClient()
        # scopes = ['https://www.googleapis.com/auth/contacts.readonly']
        # client = AuthClient(serviceName='people', scopes=scopes)
        if test.is_connected():
            self.assertTrue(test.authenticate())


if __name__ == '__main__':
    unittest.main()
