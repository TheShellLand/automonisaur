import unittest
import pandas as pd

from automon.helpers.crypto import CryptoCSV


class CryptoTest(unittest.TestCase):

    def test_crypto(self):
        data = {'data': [1, 2, 3]}
        series = pd.Series(data).rename('data')
        df = pd.DataFrame(series)
        csv = df.to_csv()

        c = CryptoCSV()
        test = '''ASSET NAME	RECEIVED DATE	COST BASIS(USD)	DATE SOLD	PROCEEDS
        BTC	10/08/20	10.00	10/10/20	10.37
        BTC	10/10/20	99.00	10/12/20	100.63
        BTC	10/13/20	201.01	10/19/20	202.47'''

        self.assertTrue(CryptoCSV())
        self.assertTrue(CryptoCSV(fake_csv=csv))
        self.assertFalse(CryptoCSV(dataframe=df).df.empty)
        self.assertEqual(type(CryptoCSV(dataframe=df).df), type(df))
        self.assertFalse(c.csv_from_string(test).empty)

        pass


if __name__ == '__main__':
    unittest.main()
