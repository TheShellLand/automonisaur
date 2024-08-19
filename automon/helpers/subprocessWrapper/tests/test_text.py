import unittest

from automon.helpers.subprocessWrapper import Run


class TestRun(unittest.TestCase):
    def test_text(self):
        run = Run()
        run.run('ls', text=True)
        self.assertEqual(type(run.stdout), bytes)


if __name__ == '__main__':
    unittest.main()
