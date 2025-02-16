import unittest

from automon.integrations.seleniumWrapper.proxies_public import *


class ProxiesTest(unittest.TestCase):

    def tests(self):
        try:
            proxy_site_spys()

            proxy_site_free_proxy_list()

            proxy_site_topproxylinks()

            proxy_get_random_proxy()

            proxy_filter_https_proxies()

            proxy_filter_https_ips_and_ports()

            proxy_filter_https_ips_and_ports_get_random()
            proxy_filter_https_ips_and_ports()

            proxy_filter_ips_and_ports()

        except:
            pass


if __name__ == '__main__':
    unittest.main()
