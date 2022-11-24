import unittest

from automon.helpers.subprocessWrapper import Run

run = Run()


class TestRun(unittest.TestCase):

    def test_su(self):
        cmd = [
            'ls',
            '-lh'
        ]
        self.assertTrue(run.run(cmd, sanitize_command=False))


if __name__ == '__main__':
    unittest.main()
