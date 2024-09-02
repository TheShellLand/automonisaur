import unittest

from automon.integrations.keepass_to_pass import KeepassClient

test = KeepassClient()


class TestKeepassClient(unittest.TestCase):
    def test_set_database_csv_path(self):
        with self.assertRaises(FileNotFoundError):
            test.set_database_csv_path('AAAA.XXXCSV')

        open('BBBB.XXXCSV', 'w').close()

        self.assertTrue(test.set_database_csv_path('BBBB.XXXCSV'))

    def test_read_database_csv(self):
        with self.assertRaises(OSError):
            test.read_database_csv('AAAA.XXXCSV')


if __name__ == '__main__':
    unittest.main()
