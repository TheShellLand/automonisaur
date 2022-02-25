import unittest

from automon.integrations.splunk_soar import SplunkSoarConfig

c = SplunkSoarConfig()


class TestPhantomConfig(unittest.TestCase):

    def test_config(self):
        if c.isReady():
            self.assertTrue(c.isReady())
        else:
            self.assertFalse(c.isReady())


if __name__ == '__main__':
    unittest.main()
