import unittest
import asyncio

from automon.integrations.google.auth import GoogleAuthClient


class MyTestCase(unittest.TestCase):
    async def test_authenticate(self):
        test = GoogleAuthClient()
        # scopes = ['https://www.googleapis.com/auth/contacts.readonly']
        # client = AuthClient(serviceName='people', scopes=scopes)
        if test.authenticate():
            self.assertTrue(asyncio.run(test.authenticate()))


if __name__ == '__main__':
    unittest.main()
