import unittest

from automon.integrations.instagram.client_browser import InstagramBrowserClient

client = InstagramBrowserClient(headless=False)
client.start()


class InstagramClientTest(unittest.TestCase):

    def test(self):

        if client.is_ready():
            client.browser.get(client.urls.domain)
            if not client.is_authenticated():
                client.authenticate()
        client.browser.quit()


if __name__ == '__main__':
    unittest.main()
