import datetime
import logging

import pandas as pd
import numpy as np
import tracemalloc

import unittest

import automon
from automon.integrations.google.sheets import GoogleSheetsClient
from automon.integrations.facebook import FacebookGroups
from automon import Logging

logging.getLogger('SeleniumBrowser').setLevel(logging.CRITICAL)
logging.getLogger('FacebookGroups').setLevel(logging.CRITICAL)
logging.getLogger('ConfigChrome').setLevel(logging.ERROR)
logging.getLogger('RequestsClient').setLevel(logging.INFO)

tracemalloc.start()

log = Logging(level=Logging.INFO)


def get_facebook_info(url: str):
    if not url:
        return {}

    group = FacebookGroups(
        url=url_cleaner(url=url)
    )
    # group.start(headless=False)
    group.start(headless=True)
    group.get_about()
    # if not group.privacy_details:
    #     close = group._browser.wait_for(group.xpath_popup_close)
    #     group._browser.action_click(close)
    #     about = group._browser.wait_for(group.xpath_about)
    #     group._browser.action_click(about)

    return group.to_dict()


def url_cleaner(url: str):
    if url[-1] == '/':
        url = url[:-1]
    return url


class MyTestCase(unittest.TestCase):
    def test_authenticate(self):
        spreadsheetId = '1isrvjU0DaRijEztByQuT9u40TaCOCwdaLAXgGmKHap8'
        test = GoogleSheetsClient(
            spreadsheetId=spreadsheetId,
            worksheet='Automated Count WIP',
        )

        if not test.authenticate():
            return

        def merge_urls():
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

            df_Shelley = pd.DataFrame(data=links, columns=['url'])

            test.get()
            test.get_values(
                range='Automated Count WIP!A:Z'
            )

            sheet_values = test.values
            sheet_columns = sheet_values[0]
            sheet_data = sheet_values[1:]

            df = pd.DataFrame(data=sheet_data, columns=sheet_columns)
            df = df.dropna(subset=['url'])

            # merge both lists or urls
            df = pd.merge(df, df_Shelley, how='outer', on='url')
            df = df.drop_duplicates(subset=['url'], keep='first')
            return df

        def batch_processing(index: int, df: pd.DataFrame):
            df_results = df['url'].dropna().apply(
                lambda url: get_facebook_info(url=url)
            )
            df_results = pd.DataFrame(df_results.tolist())

            todays_date = datetime.datetime.now().date()

            df = df.reset_index()
            df = df.drop('index', axis=1)

            # create columns
            df[f'url'] = df_results['url']
            df[f'{todays_date}'] = df_results['members_count']
            df[f'title'] = df_results['title']
            df[f'content_unavailable'] = df_results['content_unavailable']
            df[f'creation_date'] = df_results['creation_date']
            df[f'creation_date_timestamp'] = df_results['creation_date_timestamp']
            df[f'history'] = df_results['history']
            df[f'members_count'] = df_results['members_count']
            df[f'posts_monthly_count'] = df_results['posts_monthly_count']
            df[f'posts_today_count'] = df_results['posts_today_count']
            df[f'privacy'] = df_results['privacy']
            df[f'visible'] = df_results['visible']

            # set dtype to Int32
            df[f'{todays_date}'] = df[f'{todays_date}'].astype('Int32')
            df[f'creation_date_timestamp'] = df[f'creation_date_timestamp'].astype('Int32')
            df[f'members_count'] = df[f'members_count'].astype('Int32')
            df[f'posts_monthly_count'] = df[f'posts_monthly_count'].astype('Int32')
            df[f'posts_today_count'] = df[f'posts_today_count'].astype('Int32')

            # order columns
            columns = [
                'url',
                'title',
                'creation_date',
                'creation_date_timestamp',
                'history',
                'privacy',
                'visible',
                'content_unavailable',
                'posts_monthly_count',
                'posts_today_count',
                'members_count',
            ]

            # add all other dates
            df_columns = df.columns.tolist()
            columns.extend(
                [x for x in df_columns if x not in columns]
            )

            # finally add today's date
            if f'{todays_date}' not in columns:
                columns.append(
                    f'{todays_date}',
                )

            df = df.loc[:, columns]
            df = df.fillna(np.nan).replace([np.nan], [None])

            sheet_index = index + 2

            update_columns = test.update(
                range=f'Automated Count WIP!A1:Z',
                values=[columns],
            )

            update = test.update(
                range=f'Automated Count WIP!A{sheet_index}:Z',
                values=[x for x in df.values.tolist()]
            )

            log.info(
                f'{[x for x in df.values.tolist()]}'
            )

            return df

        def memory_profiler():
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics("lineno")

            df_memory_profile = pd.DataFrame([
                dict(size_B=stat.size, count=stat.count, file=stat.traceback._frames[0][0],
                     file_line=stat.traceback._frames[0][1]) for stat in top_stats
            ])
            df_memory_profile.sort_values(by='size_B', ascending=False)
            df_memory_profile['size_KB'] = df_memory_profile['size_B'].apply(
                lambda B: round(B / 1024)
            )
            df_memory_profile['size_MB'] = df_memory_profile['size_KB'].apply(
                lambda KB: round(KB / 1024)
            )
            cols = df_memory_profile.columns.tolist()
            cols.sort()
            df_memory_profile = df_memory_profile.loc[:, cols]

            log.debug(
                f"total memory used: {df_memory_profile['size_MB'].sum()} MB; "
                f'most memory used: '
                f'{df_memory_profile.iloc[0].to_dict()}'
            )

            return df_memory_profile

        # start processing
        test.get_values(
            range='Automated Count WIP!A:Z'
        )

        sheet_values = test.values
        sheet_columns = sheet_values[0]
        sheet_data = sheet_values[1:]

        df = pd.DataFrame(data=sheet_data, columns=sheet_columns)
        df = df.dropna(subset=['url'])

        BATCH_SIZE = 1

        i = 0 + 6146
        i = 0
        while i < len(df):
            df_batch = df[i:i + BATCH_SIZE]
            try:
                df_batch = batch_processing(index=i, df=df_batch)
                df_memory = memory_profiler()
            except Exception as e:
                df_memory = memory_profiler()
                pass
            i += 1

            pass

        pass


if __name__ == '__main__':
    unittest.main()
