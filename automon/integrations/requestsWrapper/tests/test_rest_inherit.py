import asyncio
import unittest

from automon.integrations.requestsWrapper.rest import BaseRestClient


class Inherit(BaseRestClient):

    def __init__(self):
        super().__init__()
        pass


class Client(unittest.TestCase):
    def test_get(self):
        self.assertTrue(asyncio.run(Inherit().get(url='https://1.1.1.1')))


if __name__ == '__main__':
    unittest.main()
