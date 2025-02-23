import unittest

from automon.integrations.google.gmail import v1


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(v1.Api().url, 'https://gmail.googleapis.com/gmail/v1')
        self.assertEqual(v1.UsersDrafts(userId='AAAABBBB').create,
                         'https://gmail.googleapis.com/gmail/v1/users/AAAABBBB/drafts')
        self.assertEqual(v1.Users(userId='AAAABBBB').getProfile,
                         'https://gmail.googleapis.com/gmail/v1/users/AAAABBBB/profile')

        pass


if __name__ == '__main__':
    unittest.main()
