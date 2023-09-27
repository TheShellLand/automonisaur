import unittest

import pandas as pd

from automon.integrations.google.sheets import GoogleSheetsClient

SHEET_NAME = 'Copy of Automated Count DO NOT EDIT'


class MyTestCase(unittest.TestCase):
    def test_authenticate(self):
        sheets_client = GoogleSheetsClient(
            worksheet=SHEET_NAME,
        )

        if not sheets_client.authenticate():
            return

        sheets_client.get_values(
            range=f'{SHEET_NAME}!A:Z'
        )

        sheet_values = sheets_client.values
        sheet_columns = sheet_values[0]
        sheet_data = sheet_values[1:]

        df = pd.DataFrame(data=sheet_data, columns=sheet_columns)
        df = df.dropna(subset=['url'])
        # set df index to match google sheet index numbering
        df.index = df.index + 2

        sheets_client.clear(
            range=f'{SHEET_NAME}!8:5',
        )

        pass


if __name__ == '__main__':
    unittest.main()
