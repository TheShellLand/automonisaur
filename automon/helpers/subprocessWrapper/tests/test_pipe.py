import unittest

from automon.helpers.subprocessWrapper import Run


class TestRun(unittest.TestCase):
    def test_pip(self):
        run = Run()

        run.run('ls | grep eric', shell=True, text=True)
        pass


if __name__ == '__main__':
    unittest.main()
