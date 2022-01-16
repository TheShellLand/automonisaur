import unittest

from automon.integrations.cryptocurrency import CryptoAccounting, Robinhood, Coinbase

with open('empty.csv', 'w') as f:
    f.write('''ASSET NAME,RECEIVED DATE,COST BASIS(USD),DATE SOLD,PROCEEDS''')

with open('robinhood.csv', 'w') as f:
    f.write('''Provider: Robinhood Crypto LLC,,,
Disclaimer: ,,,,
,,,,
,,,,
,,,,
,,,,
ASSET NAME,RECEIVED DATE,COST BASIS(USD),DATE SOLD,PROCEEDS''')


class CryptoAccountingTest(unittest.TestCase):
    c = CryptoAccounting()

    def test_CryptoAccounting(self):
        self.assertTrue(CryptoAccounting())

    def test_auto_detect(self):
        self.assertTrue(self.c.auto_detect('robinhood.csv'))
        self.assertFalse(self.c.auto_detect('empty.csv'))

    def test_walk(self):
        self.assertTrue(CryptoAccounting('.'))

    def test_robinhood(self):
        self.assertTrue(CryptoAccounting().robinhood('robinhood.csv'))

    def test_other(self):
        self.assertTrue(CryptoAccounting().other('empty.csv'))


class RobinhoodTest(unittest.TestCase):
    def test_Robinhood(self):
        self.assertTrue(Robinhood)


class CoinbaseTest(unittest.TestCase):
    def test_Coinbase(self):
        self.assertTrue(Coinbase)


if __name__ == '__main__':
    unittest.main()
