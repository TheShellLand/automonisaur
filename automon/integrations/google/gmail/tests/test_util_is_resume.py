import unittest

from automon.integrations.google.gmail import GoogleGmailClient

from .thread import thread
from ..classes import *

gmail = GoogleGmailClient()

# gmail.config.add_gmail_scopes()
gmail.config.add_scopes(
    ["https://mail.google.com/"]
)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        t = GmailThread(thread)

        pass


if __name__ == '__main__':
    unittest.main()
