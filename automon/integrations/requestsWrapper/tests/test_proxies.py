import unittest

from automon.integrations.requestsWrapper import RequestsClient
from automon.integrations.requestsWrapper import RequestsConfig

r = RequestsClient()
r.config.use_random_proxies = True

working_proxies = []


class Test(unittest.TestCase):
    def test_get(self):
        response = r.get('https://one.one.one.one/')

        if response.status_code:
            print(f'OK :: {response.proxies} :: {response.content} :: {response.status_code=}')
            working_proxies.append(r.proxies)
            pass


if __name__ == '__main__':
    unittest.main()
