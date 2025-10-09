import unittest

from automon.integrations.xsoar import XSOARClient

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, ERROR

LoggingClient.logging.getLogger('urllib3.connectionpool').setLevel(ERROR)


class MyTestCase(unittest.TestCase):
    client = XSOARClient()

    if client.is_ready():
        def test_auth(self):
            entryid = ''
            result = self.client.download_file(entryid=entryid)
            pass


if __name__ == '__main__':
    unittest.main()
