import unittest

from automon.integrations.google.gmail.api.v1 import *


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(Api().url, 'https://gmail.googleapis.com/gmail/v1')
        self.assertEqual(UsersDrafts(userId='AAAABBBB').create,
                         'https://gmail.googleapis.com/gmail/v1/users/AAAABBBB/drafts')
        self.assertEqual(Users(userId='AAAABBBB').getProfile,
                         'https://gmail.googleapis.com/gmail/v1/users/AAAABBBB/profile')

        pass


if __name__ == '__main__':
    unittest.main()
