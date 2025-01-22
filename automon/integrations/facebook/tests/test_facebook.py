import unittest

import automon.integrations.facebook.groups


class MyTestCase(unittest.TestCase):
    def test_something(self):
        client = automon.integrations.facebook.FacebookGroups()

        if client._browser.webdriver:
            client.start(headless=False)

        pass


if __name__ == '__main__':
    unittest.main()
