import unittest

from automon.healthcheck import Healthcheck


class HealthcheckTest(unittest.TestCase):
    def test_Healthcheck(self):
        self.assertTrue(Healthcheck())
        self.assertFalse(Healthcheck().up)
        self.assertFalse(Healthcheck().check())

# if __name__ == '__main__':
#     unittest.main()
