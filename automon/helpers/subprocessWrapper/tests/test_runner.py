import unittest

from automon.helpers import Run


class RunTest(unittest.TestCase):
    r = Run()

    def test_Run(self):
        self.assertTrue(Run)
        self.assertFalse(Run())

    def test_set_command(self):
        self.assertTrue(self.r.set_command('which'))
        self.assertFalse(self.r.set_command(''))

    def test_which(self):
        self.assertTrue(self.r.which('which'))
        self.assertFalse(self.r.which(''))

    def test_run_command(self):
        self.assertTrue(self.r.run_command('id'))
        self.assertFalse(self.r.run_command('false'))

    def test_run(self):
        self.assertTrue(self.r.run('id'))
        self.assertFalse(self.r.run('false'))


if __name__ == '__main__':
    unittest.main()
