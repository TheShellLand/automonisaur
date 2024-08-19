import unittest

from automon.liveliness import Liveliness


class LifelinessTest(unittest.TestCase):
    def test_Liveliness(self):
        self.assertTrue(Liveliness())
        self.assertFalse(Liveliness().up)
        self.assertFalse(Liveliness().check())

# if __name__ == '__main__':
#     unittest.main()
