import unittest

from automon.integrations.keepass_to_pass import (
    KeepassClient,
    PassClient
)

kc = KeepassClient()
pc = PassClient()

csv = 'keys_export.csv'


class MyTestCase(unittest.TestCase):
    def test_something(self):
        pws = kc.read_database_csv(csv)
        self.assertTrue(pws)

        for pw in pws:
            pc.save(pass_name=pw.pass_name, password=pw.to_pass())


if __name__ == '__main__':
    unittest.main()
