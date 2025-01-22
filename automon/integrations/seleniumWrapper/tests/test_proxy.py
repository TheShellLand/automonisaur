import unittest

from automon.integrations.seleniumWrapper.proxies_public import *


class ProxiesTest(unittest.TestCase):

    def test_proxy_site_spys(self):
        self.assertIsNotNone(proxy_site_spys())

    def test_proxy_site_free_proxy_list(self):
        self.assertIsNotNone(proxy_site_free_proxy_list())

    def test_proxy_get_random_proxy(self):
        self.assertIsNotNone(proxy_get_random_proxy())

    def test_proxy_filter_https_proxies(self):
        self.assertIsNotNone(proxy_filter_https_proxies())

    def test_proxy_filter_https_ips_and_ports(self):
        self.assertIsNotNone(proxy_filter_https_ips_and_ports())

    def test_proxy_filter_https_ips_and_ports_get_random(self):
        self.assertTrue(proxy_filter_https_ips_and_ports_get_random())


if __name__ == '__main__':
    unittest.main()
