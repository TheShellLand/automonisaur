import unittest
import pandas as pd

from automon.integrations.datascience import Pandas

csv_empty = '''ASSET NAME	RECEIVED DATE	COST BASIS(USD)	DATE SOLD	PROCEEDS'''

csv_test = '''ASSET NAME	RECEIVED DATE	COST BASIS(USD)	DATE SOLD	PROCEEDS
BTC	10/08/20	10.00	10/10/20	10.37
BTC	10/10/20	99.00	10/12/20	100.63
BTC	10/13/20	201.01	10/19/20	202.47'''

data_empty = {}
data = {'data': [1, 2, 3]}

series_empty = pd.Series(data_empty).rename('data')
series = pd.Series(data).rename('data')
df = pd.DataFrame(series)
csv = df.to_csv()

with open('empty.csv', 'w') as f:
    f.write(csv_empty)

with open('test.csv', 'w') as f:
    f.write(csv_test)


class PandasTest(unittest.TestCase):
    pd = Pandas()

    def test_Pandas(self):
        self.assertTrue(Pandas)
        self.assertTrue(Pandas())

    def test_read_csv(self):
        self.assertTrue(Pandas().read_csv('empty.csv').empty)
        self.assertFalse(Pandas().read_csv('test.csv').empty)

    def test_csv_from_string(self):
        self.assertTrue(Pandas().csv_from_string(csv_empty).empty)
        self.assertFalse(Pandas().csv_from_string(csv_test).empty)

    def test_export_csv(self):
        test = Pandas()
        test.df = df
        self.assertTrue(test.export_csv())

    def test_Series(self):
        self.assertTrue(Pandas().Series(data=data_empty).empty)
        self.assertFalse(Pandas().Series(data=data).empty)

    def test_DataFrame(self):
        self.assertTrue(Pandas().DataFrame(data=series_empty).empty)
        self.assertFalse(Pandas().DataFrame(data=series).empty)


if __name__ == '__main__':
    unittest.main()
