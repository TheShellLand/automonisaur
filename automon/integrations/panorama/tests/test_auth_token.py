import unittest

from automon.integrations.panorama import PanoramaClient


class MyTestCase(unittest.TestCase):
    client = PanoramaClient()

    def test_something(self):
        if self.client.is_ready:
            self.client.get_firewall_device()


if __name__ == '__main__':
    unittest.main()
