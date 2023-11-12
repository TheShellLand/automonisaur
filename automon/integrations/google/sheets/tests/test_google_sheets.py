import datetime
import logging
import automon
import tracemalloc

import pandas as pd
import numpy as np

from automon.log import logger
from automon.helpers.sleeper import Sleeper
from automon.integrations.facebook import FacebookGroups
from automon.integrations.google.sheets import GoogleSheetsClient

logging.getLogger('google_auth_httplib2').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.common.service').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.common.selenium_manager').setLevel(logging.ERROR)

logging.getLogger('automon.integrations.seleniumWrapper.browser').setLevel(logging.DEBUG)
logging.getLogger('automon.integrations.seleniumWrapper.config_webdriver_chrome').setLevel(logging.DEBUG)
logging.getLogger('automon.integrations.facebook.groups').setLevel(logging.DEBUG)
logging.getLogger('automon.integrations.requestsWrapper.client').setLevel(logging.INFO)

tracemalloc.start()

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)

SHEET_NAME = 'Automated Count DO NOT EDIT'
SHEET_NAME_INGEST = 'URLS TO INGEST'

sheets_client = GoogleSheetsClient(
    worksheet=SHEET_NAME,
)


def get_facebook_info(url: str):
    if not url:
        return {}

    group = FacebookGroups(
        url=url_cleaner(url=url)
    )
    # group.start(headless=False)
    group.start(headless=True)
    group.get_about()

    return group.to_dict()


def url_cleaner(url: str):
    if not url:
        return
    if url[-1] == '/':
        url = url[:-1]
    return url


def merge_urls():
    sheets_client.get(
        ranges='AUG23 AUDIT!A:Z',
        fields="sheets/data/rowData/values/hyperlink",
    )

    data = sheets_client.response['sheets'][0]['data'][0]['rowData']
    # expand nested data
    links = []
    for x in data:
        if x:
            links.append(
                x['values'][0]['hyperlink']
            )

    df_Shelley = pd.DataFrame(data=links, columns=['url'])

    sheets_client.get()
    sheets_client.get_values(
        range=f'{SHEET_NAME}!A:Z'
    )

    sheet_values = sheets_client.values
    sheet_columns = sheet_values[0]
    sheet_data = sheet_values[1:]

    df = pd.DataFrame(data=sheet_data, columns=sheet_columns)
    df = df.dropna(subset=['url'])

    # merge both lists or urls
    df = pd.merge(df, df_Shelley, how='outer', on='url')
    df = df.drop_duplicates(subset=['url'], keep='first')
    return df


def batch_processing(sheet_index: int, df: pd.DataFrame):
    df_results = df['url'].dropna().apply(
        lambda url: get_facebook_info(url=url)
    )
    df_results = pd.DataFrame(df_results.tolist())

    df = df.reset_index()

    todays_date = datetime.datetime.now().date()
    monthly = f'{todays_date.year}-{todays_date.month}'

    # create columns
    df[f'url'] = df_results['url']
    df[f'{monthly}'] = df_results['members_count']
    df[f'last_updated'] = monthly
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
    df[f'{monthly}'] = df[f'{monthly}'].astype('Int32')
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
        'last_updated',
        'posts_monthly_count',
        'posts_today_count',
        'members_count',
    ]

    sheet_index_df = df['index'].loc[0]
    assert sheet_index == sheet_index_df
    df = df.drop('index', axis=1)

    # add all other dates
    df_columns = df.columns.tolist()
    columns.extend(
        [x for x in df_columns if x not in columns]
    )

    # finally add today's date
    if f'{monthly}' not in columns:
        columns.append(
            f'{monthly}',
        )

    df = df.loc[:, columns]
    df = df.fillna(np.nan).replace([np.nan], [None])

    update_columns = sheets_client.update(
        range=f'{SHEET_NAME}!A1:Z',
        values=[columns],
    )

    update = sheets_client.update(
        range=f'{SHEET_NAME}!A{sheet_index_df}:Z',
        values=[x for x in df.values.tolist()]
    )

    log.info(f'{sheet_index_df}: {[x for x in df.values.tolist()]}')

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


def main():
    if not sheets_client.authenticate():
        return

    # merge urls from audit sheet
    # df_audit = merge_urls()
    # df_audit = df_audit.fillna(np.nan).replace([np.nan], [None])
    # rows = []
    # rows.append(df_audit.columns.tolist())
    # rows.extend([x for x in df_audit.values.tolist()])
    # update = sheets_client.update(
    #     range=f'{SHEET_NAME}!A:Z',
    #     values=rows
    # )

    # start processing
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

    # drop duplicates
    df_duplicates_to_delete = df[
        (df.url.duplicated(keep='first'))
    ]

    for duplicate in df_duplicates_to_delete.iterrows():
        duplicate_index, duplicate_row = duplicate

        # clear row in sheet
        range = f'{SHEET_NAME}!{duplicate_index}:{duplicate_index}'
        result = sheets_client.clear(range=range)
        # max 60/min
        Sleeper.seconds(seconds=1)
        log.info(result)
        df = df.drop(duplicate_index)

    # ingest urls from SHEET_NAME_INGEST
    sheets_client.get_values(
        range=f'{SHEET_NAME_INGEST}!A:Z'
    )
    ingest_sheet_values = sheets_client.values
    if ingest_sheet_values:
        ingest_sheet_values = [x[0] if x else [] for x in ingest_sheet_values]
        ingest_sheet_values = [url_cleaner(x) for x in ingest_sheet_values]
    df_ingest_sheet_values = pd.DataFrame(ingest_sheet_values)
    df_ingest_sheet_values.index = df_ingest_sheet_values.index + 1

    for ingest_data in df_ingest_sheet_values.iterrows():
        ingest_index, ingest_url = ingest_data
        ingest_url = ingest_url[0]

        if ingest_url not in df['url'].values:
            ingest_series = pd.Series({'url': ingest_url}).to_frame().T
            index_add_url = df.index[-1] + 1
            df.loc[index_add_url] = {'url': ingest_url}

            df.loc[index_add_url] = df.loc[index_add_url].fillna(np.nan).replace([np.nan], [None])

            values = [[x for x in df.loc[index_add_url].values.tolist()]]

            update = sheets_client.update(
                range=f'{SHEET_NAME}!A{index_add_url}:Z',
                values=values
            )

            log.info(
                f'{index_add_url}: {values}'
            )

        # clear url from ingest sheet
        range = f'{SHEET_NAME_INGEST}!{ingest_index}:{ingest_index}'
        clear = sheets_client.clear(range=range)
        log.info(f'{clear}')

    # start updating
    for data in df.iterrows():
        data_index, data_row = data

        df_batch = df.loc[data_index:data_index]

        # skip if last_updated is the current month
        todays_date = datetime.datetime.now().date()
        last_updated = f'{todays_date.year}-{todays_date.month}'
        if df_batch['last_updated'].iloc[0] == last_updated:
            # log.debug(f'skipping {data_index}, {data_row.to_dict()}')
            continue

        batch_result = batch_processing(sheet_index=data_index, df=df_batch)

        try:
            batch_result = batch_processing(sheet_index=data_index, df=df_batch)
            df_memory = memory_profiler()
        except Exception as e:
            df_memory = memory_profiler()
            log.error(f'{e}')

    pass


if __name__ == '__main__':
    main()
