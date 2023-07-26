import unittest

from automon.integrations.google.auth import AuthClient


class MyTestCase(unittest.TestCase):
    def test_authenticate(self):
        test = AuthClient()
        # scopes = ['https://www.googleapis.com/auth/contacts.readonly']
        # client = AuthClient(serviceName='people', scopes=scopes)
        if test.authenticate():
            self.assertTrue(test.authenticate())


if __name__ == '__main__':
    unittest.main()
