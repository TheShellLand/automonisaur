import unittest

from automon.integrations.seleniumWrapper.proxies_public import *


class ProxiesTest(unittest.TestCase):

    def test_proxy_site_spys(self):
        proxy_site_spys()

    def test_proxy_site_free_proxy_list(self):
        proxy_site_free_proxy_list()

    def test_proxy_site_topproxylinks(self):
        proxy_site_topproxylinks()

    def test_proxy_get_random_proxy(self):
        proxy_get_random_proxy()

    def test_proxy_filter_https_proxies(self):
        proxy_filter_https_proxies()

    def test_proxy_filter_https_ips_and_ports(self):
        proxy_filter_https_ips_and_ports()

    def test_proxy_filter_https_ips_and_ports_get_random(self):
        proxy_filter_https_ips_and_ports_get_random()
        proxy_filter_https_ips_and_ports()

    def test_proxy_filter_ips_and_ports(self):
        proxy_filter_ips_and_ports()


if __name__ == '__main__':
    unittest.main()
