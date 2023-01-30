import unittest

from automon.integrations.splunk_soar import SplunkSoarConfig

c = SplunkSoarConfig()


class TestPhantomConfig(unittest.TestCase):

    def test_config(self):
        if c.is_ready:
            self.assertTrue(c.is_ready)
        else:
            self.assertFalse(c.is_ready)


if __name__ == '__main__':
    unittest.main()
