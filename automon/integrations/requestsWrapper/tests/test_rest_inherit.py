import unittest

from automon.integrations.requestsWrapper.rest import BaseRestClient


class Test(BaseRestClient):

    def __init__(self):
        BaseRestClient.__init__(self)
        pass


class Client(unittest.TestCase):
    def test_get(self):
        Test().get(url='https://1.1.1.1')


if __name__ == '__main__':
    unittest.main()
