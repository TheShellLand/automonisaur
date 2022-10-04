import unittest

from automon.helpers.subprocessWrapper import Run

run = Run()


class TestRun(unittest.TestCase):
    def test_false(self):
        self.assertFalse(run.run(''))


if __name__ == '__main__':
    unittest.main()
