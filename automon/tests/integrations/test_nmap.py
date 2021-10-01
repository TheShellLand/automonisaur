import unittest

from automon.integrations.nmap import Nmap, NmapConfig


class NmapConfigTest(unittest.TestCase):
    def test_config(self):
        self.assertTrue(NmapConfig())


class NmapTest(unittest.TestCase):

    def test_run(self):
        if Nmap().ready:
            self.assertTrue(Nmap().run('localhost'))
            self.assertTrue(Nmap().run('localhost', output=False))

    def test_nmap(self):
        nmap = Nmap()

        if Nmap().ready:
            self.assertTrue(Nmap().nmap(command='localhost'))
            self.assertTrue(Nmap().nmap(command='localhost', output=False))
            nmap.ready = False
            self.assertFalse(nmap.nmap(command='localhosta'))

    def test_scan(self):
        nmap = Nmap()

        if Nmap().ready:
            self.assertTrue(Nmap().scan(command='localhost'))
            self.assertTrue(Nmap().scan(command='localhost', output=False))
            nmap.ready = False
            self.assertFalse(nmap.scan(command='localhosta'))

    def test_results(self):
        nmap = Nmap()

        if Nmap().ready:
            self.assertTrue(nmap.scan('-sn localhost'))
            # self.assertTrue(nmap.scan(' 1.1.1.1'))
            self.assertTrue(nmap.scan('-p 80,443 localhost'))
            self.assertTrue(nmap.scan('-n -p 80,443 localhost localhost'))


if __name__ == '__main__':
    unittest.main()
