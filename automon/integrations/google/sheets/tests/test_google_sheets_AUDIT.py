import datetime
import pandas as pd

import unittest

from automon.integrations.google.sheets import GoogleSheetsClient
from automon.integrations.facebook import FacebookGroups


def get_facebook_info(url: str):
    group = FacebookGroups()
    # group.start(headless=False)
    if group.start():
        group.get(url=url)
        if not group.privacy_details:
            close = group._browser.wait_for_element(value=group._xpath_popup_close, by=group._browser.by.XPATH)
            close.click()
            about = group._browser.wait_for_element(value=group._xpath_about, by=group._browser.by.XPATH)
            about.click()

        return group.to_dict()


class MyTestCase(unittest.TestCase):
    def test_authenticate(self):
        spreadsheetId = '1isrvjU0DaRijEztByQuT9u40TaCOCwdaLAXgGmKHap8'
        test = GoogleSheetsClient(
            spreadsheetId=spreadsheetId,
            worksheet='AUDIT list Shelley',
            range='AUDIT list Shelley!A:B'
        )

        try:
            test.authenticate()
        except Exception as error:
            return

        test.get_values(
            range='AUDIT list Shelley!A:Z',
        )
        test.get(
            ranges='AUDIT list Shelley!A:Z',
            fields="sheets/data/rowData/values/hyperlink",
        )

        data = test.response['sheets'][0]['data'][0]['rowData']
        # expand nested data
        links = []
        for x in data:
            if x:
                links.append(
                    x['values'][0]['hyperlink']
                )

        df = pd.DataFrame(links)

        pass


if __name__ == '__main__':
    unittest.main()
