import unittest

from automon.helpers.subprocessWrapper import Run
from automon.helpers.subprocessWrapper.exceptions import *

run = Run()


class TestRun(unittest.TestCase):
    def test_pip(self):
        self.assertRaises(
            NotSupportedCommand,
            run.run,
            'ls | grep eric', shell=True, text=True,
        )


if __name__ == '__main__':
    unittest.main()
