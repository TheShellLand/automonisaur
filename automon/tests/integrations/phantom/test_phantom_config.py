import unittest

from automon.integrations.phantom import PhantomConfig


class TestPhantomConfig(unittest.TestCase):
    c = PhantomConfig()

    def test_config(self):
        self.assertTrue(self.c)


if __name__ == '__main__':
    unittest.main()
