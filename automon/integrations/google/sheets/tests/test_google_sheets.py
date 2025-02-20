import traceback

import pandas
import automon
import profile
import logging
import datetime
import warnings
import tracemalloc

import numpy as np
import selenium.common.exceptions
import pandas._libs.missing

from automon.helpers.sleeper import Sleeper
from automon.integrations.facebook import FacebookGroups
from automon.helpers.loggingWrapper import LoggingClient, DEBUG
from automon.integrations.google.sheets import GoogleSheetsClient

logging.getLogger('urllib3.util.retry').setLevel(logging.ERROR)
logging.getLogger('google_auth_httplib2').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.common.service').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.common.driver_finder').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.common.selenium_manager').setLevel(logging.ERROR)

logging.getLogger('automon.integrations.seleniumWrapper.browser').setLevel(logging.CRITICAL)
logging.getLogger('automon.integrations.seleniumWrapper.config').setLevel(logging.CRITICAL)
logging.getLogger('automon.integrations.seleniumWrapper.webdriver_chrome').setLevel(logging.ERROR)
logging.getLogger('automon.integrations.google.sheets.client').setLevel(logging.INFO)
logging.getLogger('automon.integrations.facebook.groups').setLevel(logging.DEBUG)
logging.getLogger('automon.integrations.requestsWrapper.client').setLevel(logging.ERROR)
logging.getLogger('automon.helpers.sleeper').setLevel(logging.INFO)

tracemalloc.start()

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)

DAYS_REQUIRED_BEFORE_UPDATING_AGAIN = 45

BROWSER_HEADLESS = True
BROWSER_USERAGENT_RANDOMIZER = True

FACEBOOK_RATE_LIMITING = False
FACEBOOK_PROXY_ENABLED = True
FACEBOOK_PROXY_RANDOM = True
FACEBOOK_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'

SHEET_NAME = 'Automated Count DO NOT EDIT'
SHEET_NAME_INGEST = 'URLS TO INGEST'
# TODO: implement deleting urls
SHEET_NAME_DELETE = 'URLS TO DELETE'

sheets_client = GoogleSheetsClient(
    worksheet=SHEET_NAME,
)

facebook_group_client = FacebookGroups()
facebook_group_client.RATE_LIMITING = FACEBOOK_RATE_LIMITING
facebook_group_client.BROWSER_HEADLESS = BROWSER_HEADLESS
facebook_group_client.PROXY_ENABLED = FACEBOOK_PROXY_ENABLED
facebook_group_client.PROXY_RANDOM = FACEBOOK_PROXY_RANDOM
facebook_group_client.USER_AGENT_STRING = FACEBOOK_USER_AGENT


def get_facebook_info(url: str, facebook_group_client: FacebookGroups) -> dict:
    logger.info(f'[get_facebook_info] :: {url=}')
    try:
        return facebook_group_client.get_facebook_info(url=url)
    except Exception as error:
        traceback.print_exc()
        raise Exception(f'[get_facebook_info] :: {error=}')


def merge_urls():
    sheets_client.get(
        ranges='AUG23 AUDIT!A:BB',
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

    df_Shelley = pandas.DataFrame(data=links, columns=['url'])

    sheets_client.get()
    sheets_client.get_values(
        range=f'{SHEET_NAME}!A:BB'
    )

    sheet_values = sheets_client.values
    sheet_columns = sheet_values[0]
    sheet_data = sheet_values[1:]

    df = pandas.DataFrame(data=sheet_data, columns=sheet_columns)
    df = df.dropna(subset=['url'])

    # merge both lists or urls
    df = pandas.merge(df, df_Shelley, how='outer', on='url')
    df = df.drop_duplicates(subset=['url'], keep='first')
    return df


def batch_processing(sheet_index: int, df: pandas.DataFrame) -> pandas.DataFrame:
    # df_results = df['url'].dropna().apply(
    #     lambda url: get_facebook_info(url=url)
    # )

    df_index = df['url'].dropna().index
    df_url = df['url'].dropna().iloc[0]

    facebook_group_client.set_url(df_url)

    if not facebook_group_client._browser.webdriver:
        facebook_group_client.start(
            set_page_load_timeout=2
        )

    try:
        df_results = get_facebook_info(url=df_url, facebook_group_client=facebook_group_client)

    except Exception as error:
        # traceback.print_exc()
        logger.error(f'[batch_processing] :: error :: {error}')
        raise error

    if not df_results['members'][0]:
        logger.error(f"[batch_processing] :: {df_results['members']=}")

        if df_results['check_blocked_by_login'][0] or df_results['check_browser_not_supported'][0]:
            logger.error(f"[batch_processing] :: {df_results['check_blocked_by_login']=}")
            logger.error(f"[batch_processing] :: {df_results['check_browser_not_supported']=}")
            logger.error(f'[batch_processing] :: failed to parse site. skipping.')
            return pandas.DataFrame()

        if not df_results['check_content_unavailable'][0]:
            raise Exception(f'[batch_processing] :: likely failed to open site. skipping.')

    df_results = pandas.DataFrame([df_results])

    df = df.reset_index()

    todays_date = datetime.datetime.now().date()
    monthly = f'{todays_date.year}-{todays_date.month}'

    # create columns
    df[f'url'] = df_results['url'][0]
    df[f'{monthly}'] = df_results['members_count'][0]
    df[f'last_updated'] = monthly
    df[f'title'] = df_results['title'][0]
    df[f'content_unavailable'] = df_results['check_content_unavailable'][0]
    df[f'creation_date'] = df_results['creation_date'][0]
    df[f'creation_date_timestamp'] = df_results['creation_date_timestamp'][0]
    df[f'history'] = df_results['history'][0]
    df[f'members_count'] = df_results['members_count'][0]
    df[f'posts_monthly_count'] = df_results['posts_monthly_count'][0]
    df[f'posts_today_count'] = df_results['posts_today_count'][0]
    df[f'privacy'] = df_results['privacy'][0]
    df[f'visible'] = df_results['visible'][0]

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

    assert df['url'].iloc[0] == df_results['url'].iloc[0]

    sheet_index_df = df['index'].loc[0]
    assert sheet_index == sheet_index_df
    df = df.drop(columns='index')

    # add all other columns
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

    types_to_skip = [
        pandas._libs.missing.NAType,
    ]

    if type(df[f'members_count'][0]) in types_to_skip:
        pass
    elif not df[f'members_count'][0]:
        pass

    # Google Sheets API expects empty values to be None
    # TODO: DeprecationWarning: The truth value of an empty array is ambiguous. Returning False, but in future this will result in an error. Use `array.size > 0` to check that an array is not empty.
    df = df.map(
        lambda x: None if pandas.isna(x) else x).map(
        lambda x: None if not x else x
    )

    update_columns = sheets_client.update(
        range=f'{SHEET_NAME}!A1:BB',
        values=[columns],
    )

    update = sheets_client.update(
        range=f'{SHEET_NAME}!A{sheet_index_df}:BB',
        values=[x for x in df.values.tolist()]
    )

    logger.info(f'[batch_processing] :: {sheet_index_df}: {[x for x in df.values.tolist()]}')

    return df


def memory_profiler():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")

    df_memory_profile = pandas.DataFrame([
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

    logger.debug(
        f"[memory_profiler] "
        f"total memory used: {df_memory_profile['size_MB'].sum()} MB; "
        f'most memory used: '
        f'{df_memory_profile.iloc[0].to_dict()}'
    )

    return df_memory_profile


def expensive_state_keeping():
    """fetch sheet data"""
    if not sheets_client.authenticate():
        return

    # merge urls from audit sheet
    # df_audit = merge_urls()
    # df_audit = df_audit.fillna(np.nan).replace([np.nan], [None])
    # rows = []
    # rows.append(df_audit.columns.tolist())
    # rows.extend([x for x in df_audit.values.tolist()])
    # update = sheets_client.update(
    #     range=f'{SHEET_NAME}!A:BB',
    #     values=rows
    # )

    # start processing
    sheets_client.get_values(
        range=f'{SHEET_NAME}!A:BB'
    )

    sheet_values = sheets_client.values
    try:
        sheet_columns = sheet_values[0]
    except:
        warnings.warn(f'this is a recursive infinite loop')
        return expensive_state_keeping()
    sheet_data = sheet_values[1:]

    if sheet_columns and sheet_data:
        for row in sheet_data:
            if len(sheet_columns) > len(sheet_data[sheet_data.index(row)]):

                fix_length = row
                r = len(sheet_columns) - len(sheet_data[sheet_data.index(row)])
                for i in range(r):
                    fix_length.append(None)

                sheet_data[sheet_data.index(row)] = fix_length

    df = pandas.DataFrame(data=sheet_data, columns=sheet_columns)
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
        data_range = f'{SHEET_NAME}!{duplicate_index}:{duplicate_index}'
        result = sheets_client.clear(range=data_range)
        # max 60/min
        Sleeper.seconds(seconds=1)
        logger.info(f'[expensive_state_keeping] :: clear :: {result}')
        df = df.drop(duplicate_index)

    # ingest urls from SHEET_NAME_INGEST
    sheets_client.get_values(
        range=f'{SHEET_NAME_INGEST}!A:BB'
    )
    ingest_sheet_values = sheets_client.values
    if ingest_sheet_values:
        ingest_sheet_values = [x[0] if x else [] for x in ingest_sheet_values]
        ingest_sheet_values = [facebook_group_client.url_cleaner(x) for x in ingest_sheet_values]
    df_ingest_sheet_values = pandas.DataFrame(ingest_sheet_values)
    df_ingest_sheet_values.index = df_ingest_sheet_values.index + 1

    for ingest_data in df_ingest_sheet_values.iterrows():
        ingest_index, ingest_url = ingest_data
        ingest_url = ingest_url[0]

        if ingest_url not in df['url'].values:
            ingest_series = pandas.Series({'url': ingest_url}).to_frame().T
            index_add_url = df.index[-1] + 1
            df.loc[index_add_url] = {'url': ingest_url}

            df.loc[index_add_url] = df.loc[index_add_url].fillna(np.nan).replace([np.nan], [None])

            values = [[x for x in df.loc[index_add_url].values.tolist()]]

            update = sheets_client.update(
                range=f'{SHEET_NAME}!A{index_add_url}:BB',
                values=values
            )

            logger.info(f'[expensive_state_keeping] :: update :: {index_add_url}: {values}')

        # clear url from ingest sheet
        data_range = f'{SHEET_NAME_INGEST}!{ingest_index}:{ingest_index}'
        clear = sheets_client.clear(range=data_range)
        logger.info(f'[expensive_state_keeping] :: clear :: {clear}')

    return df


def skip_update(last_update: str, minimum_days_passed: int) -> bool:
    DATE_TODAY = datetime.datetime.now()
    DATE_LAST_UPDATED = last_update

    if DATE_LAST_UPDATED:
        DATE_LAST_UPDATED = datetime.datetime.strptime(DATE_LAST_UPDATED, '%Y-%m')
        DAYS_LAST_UPDATED = (DATE_TODAY - DATE_LAST_UPDATED).days

        if DAYS_LAST_UPDATED < minimum_days_passed:
            return True

    return False


def progress_log(data_index: int, df: pandas.DataFrame, facebook_group_client: FacebookGroups) -> None:
    progress = int(data_index) / len(df)
    progress_remaining = round(len(df) - int(data_index))
    progress_percentage = round(progress * 100)

    remaining = len(df) - int(data_index)

    secs_remaining = facebook_group_client.average_rate() * progress_remaining
    mins_remaining = round(secs_remaining / 60)
    hours_remaining = mins_remaining / 60
    days_remaining = round(hours_remaining / 24)

    if mins_remaining:
        message_remaining = (
            f'({remaining} urls left) '
            f'({mins_remaining} mins remaining) '
            f'({days_remaining} days remaining)'
        )
    else:
        message_remaining = (
            f'({remaining} urls left) '
            f'(calculating ETA)'
        )

    logger.info(
        f'[main] :: progress :: '
        f'complete {progress_percentage}% {data_index}/{len(df)} '
        f'{message_remaining}'
    )


def main():
    df = expensive_state_keeping()

    if df is None:
        return

    ERROR_COUNTER = 0

    # start updating
    for data in df.iterrows():
        data_index = data[0]
        data_row = data[1]

        df_batch = df.loc[data_index:data_index]

        DATE_LAST_UPDATED = df_batch['last_updated'].iloc[0]

        if skip_update(last_update=DATE_LAST_UPDATED, minimum_days_passed=DAYS_REQUIRED_BEFORE_UPDATING_AGAIN):
            continue

        progress_log(data_index=data_index, df=df, facebook_group_client=facebook_group_client)

        try:
            batch_result = batch_processing(sheet_index=data_index, df=df_batch)
        except Exception as error:
            import traceback
            # traceback.print_exc()

            ERROR_COUNTER = ERROR_COUNTER + 1
            logger.error(f'[main] :: error :: {ERROR_COUNTER=} :: {error=}')

        df_memory = memory_profiler()

    facebook_group_client.quit()


if __name__ == '__main__':
    import cProfile

    pr = cProfile.Profile()
    pr.enable()

    main()

    pr.disable()
    pr.print_stats(sort='cumulative')
