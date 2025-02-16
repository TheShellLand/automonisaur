import automon
import io
import re
import pandas
import random

import automon.integrations.requestsWrapper


def proxy_site_free_proxy_list() -> pandas.DataFrame:
    url = 'https://free-proxy-list.net/'
    proxies_table = automon.integrations.requestsWrapper.RequestsClient(url)
    proxies_table.get()

    proxies_table = pandas.read_html(io.StringIO(proxies_table.text))[0]

    proxies_table['Https'] = proxies_table['Https'].apply(
        lambda x: True if x == 'yes' else x).apply(
        lambda x: False if x == 'no' else x
    )
    proxies_table['Google'] = proxies_table['Google'].apply(
        lambda x: True if x == 'yes' else x).apply(
        lambda x: False if x == 'no' else x
    )

    return proxies_table


def proxy_site_spys() -> pandas.DataFrame:
    url = 'https://spys.me/proxy.txt'
    proxies_table = automon.integrations.requestsWrapper.RequestsClient(url)
    proxies_table.get()

    MATCHED = []
    MISS_MATCHED = []

    for line in proxies_table.text.splitlines():
        # IP address:Port CountryCode-Anonymity(Noa/Anm/Hia)-SSL_support(S)-Google_passed(+)
        mapping_anonymity = dict(
            N='Noa',
            A='Anm',
            H='Hia'
        )
        mapping_ssl = dict(
            S=True
        )
        mapping_google = {
            "+": True,
            '-': False
        }

        search = re.compile(
            r'(\d+[.]\d+[.]\d+[.]\d+:\d+)\s'
            r'(\w{2})[-]?'
            r'([NAH!]{1,2})\s?[-]?'
            r'([S!]{1,2}|[-])?\s?'
            r'([-+])?\s?'
        ).fullmatch(line)

        if search:
            proxy_IpPort, proxy_CountryCode, proxy_Anonymity, proxy_SslSupport, proxy_GooglePassed = search.groups()

            mapping_search = dict(
                proxy_IpPort='IP Address and Port',
                proxy_CountryCode='Code',
                proxy_Anonymity='Anonymity',
                proxy_SslSupport='Https',
                proxy_GooglePassed='Google',
            )

            search_groups = dict(
                proxy_IpPort=proxy_IpPort,
                proxy_CountryCode=proxy_CountryCode,
                proxy_Anonymity=proxy_Anonymity,
                proxy_SslSupport=proxy_SslSupport,
                proxy_GooglePassed=proxy_GooglePassed,
            )

            search = dict(
                fullmatch=search,
                search_groups=search_groups,
                raw=line,
            )

            MATCHED.append(search)
        else:
            MISS_MATCHED.append(line)

    proxies_table = pandas.DataFrame(MATCHED)
    proxies_table = pandas.DataFrame(pandas.DataFrame(MATCHED)['search_groups'].tolist())

    proxies_table['IP Address'] = proxies_table['proxy_IpPort'].apply(
        lambda x: x.split(":")[0]
    )
    proxies_table['Port'] = proxies_table['proxy_IpPort'].apply(
        lambda x: x.split(":")[1]
    )
    proxies_table = proxies_table.drop(columns=['proxy_IpPort'])
    proxies_table['proxy_Anonymity'] = proxies_table['proxy_Anonymity'].apply(
        lambda x: (mapping_anonymity[x[0]], x[1:]) if x[1:] else mapping_anonymity[x[0]]
    )
    proxies_table['proxy_SslSupport'] = proxies_table[proxies_table['proxy_SslSupport'].notna()][
        'proxy_SslSupport'].apply(
        lambda x: (mapping_ssl[x[0]], x[1:])).apply(
        lambda x: x[0] if not x[1] else x
    )
    proxies_table['proxy_GooglePassed'] = proxies_table[proxies_table['proxy_GooglePassed'].notna()][
        'proxy_GooglePassed'].apply(
        lambda x: mapping_google[x]
    )
    proxies_table.rename(columns=mapping_search, inplace=True)

    return proxies_table


def proxy_site_topproxylinks():
    url = 'https://topproxylinks.com/'
    proxies_table = automon.integrations.requestsWrapper.RequestsClient(url)
    proxies_table.get()

    proxies_table = pandas.read_html(io.StringIO(proxies_table.text))[0]

    columns = [
        'Protocol',
        'Proxy',
        'Country',
        'ISP',
        'Anonymity Level SSL',
        'Anonymity Level Non-SSL',
        'Response Time',
        'Uptime',
        'Last Checked',
    ]

    proxies_table.columns = columns

    proxies_table['IP Address'] = proxies_table['Proxy'].apply(lambda x: f'{x}'.split(":")[0])
    proxies_table['Port'] = proxies_table['Proxy'].apply(lambda x: f'{x}'.split(":")[1])

    return proxies_table


def proxy_get_random_proxy() -> pandas.DataFrame:
    """Get proxies and return a list"""

    proxies_master_list = pandas.DataFrame()

    proxies_master_list = pandas.concat(
        [
            proxies_master_list,
            proxy_site_spys(),
            proxy_site_free_proxy_list(),
        ],
        ignore_index=True
    )

    return proxies_master_list.sample()


def proxy_master_list() -> pandas.DataFrame:
    proxies_master_list = pandas.DataFrame()

    proxies_master_list = pandas.concat(
        [
            proxies_master_list,
            proxy_site_spys(),
            proxy_site_free_proxy_list(),
            proxy_site_topproxylinks()[proxy_site_topproxylinks()['Protocol'] == 'http'],
        ],
        ignore_index=True
    )

    return proxies_master_list


def proxy_filter_https_proxies() -> pandas.DataFrame:
    filtered_master_list = proxy_master_list()
    return filtered_master_list[filtered_master_list['Https'] == True]


def proxy_filter_https_ips_and_ports() -> pandas.Series:
    filtered_master_list = proxy_filter_https_proxies()
    return filtered_master_list['IP Address'] + ":" + filtered_master_list['Port'].apply(lambda x: str(x))


def proxy_filter_ips_and_ports() -> pandas.Series:
    master_list = proxy_master_list()
    return master_list['IP Address'] + ":" + master_list['Port'].apply(lambda x: str(x))


def proxy_filter_https_ips_and_ports_get_random() -> pandas.Series:
    return proxy_filter_https_ips_and_ports().sample()
