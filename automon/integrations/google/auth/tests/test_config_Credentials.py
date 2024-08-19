import unittest
import asyncio

from automon.integrations.google.auth import GoogleAuthConfig


class MyTestCase(unittest.TestCase):
    async def test_something(self):
        test = GoogleAuthConfig()
        if await test.Credentials():
            self.assertTrue(asyncio.run(test.Credentials()))


if __name__ == '__main__':
    unittest.main()
