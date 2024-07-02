import asyncio
import unittest

from automon.integrations.xsoar import XSOARClient


class MyTestCase(unittest.TestCase):
    test = XSOARClient()

    if asyncio.run(test.is_ready()):
        def test_auth(self):
            result = asyncio.run(self.test.reports())
            pass


if __name__ == '__main__':
    unittest.main()
