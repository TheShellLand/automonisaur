import unittest

from automon.integrations.nmap import Nmap, NmapConfig


class NmapConfigTest(unittest.TestCase):
    def test_config(self):
        self.assertTrue(NmapConfig())


class NmapTest(unittest.TestCase):

    def test_run(self):
        if Nmap().ready:
            self.assertTrue(Nmap().run('-n localhost', output=False))
            self.assertTrue(Nmap().run('-n localhost', output=False))

    def test_output(self):
        n = Nmap()

        if n.ready:
            self.assertTrue(n.run('-n 127.0.0.1'))
            self.assertTrue(len(n) > 0)

    def test_output_file(self):
        if Nmap().ready:
            self.assertTrue(Nmap().run('-n 127.0.0.1', cleanup=False))
            self.assertTrue(Nmap().run('-n 127.0.0.1', cleanup=True))

    def test_nmap(self):
        nmap = Nmap()

        if Nmap().ready:
            self.assertTrue(Nmap().nmap(command='-n localhost', output=False))
            self.assertTrue(Nmap().nmap(command='-n 127.0.0.1', output=False))
            self.assertTrue(Nmap().nmap(command='-n localhost', output=False))
            nmap.ready = False
            self.assertFalse(nmap.nmap(command='localhosta', output=False))

    def test_scan(self):
        nmap = Nmap()

        if Nmap().ready:
            self.assertTrue(Nmap().scan(command='-n localhost', output=False))
            self.assertTrue(Nmap().scan(command='-n localhost', output=False))
            nmap.ready = False
            self.assertFalse(nmap.scan(command='localhosta', output=False))

    def test_results(self):
        nmap = Nmap()

        if Nmap().ready:
            self.assertTrue(nmap.scan('-sn -n localhost', output=False))
            self.assertTrue(nmap.scan('-n -p 80,443 localhost', output=False))
            self.assertTrue(nmap.scan('-n -p 80,443 localhost localhost', output=False))


if __name__ == '__main__':
    unittest.main()
