import automon
import io
import re
import pandas
import random

import automon.integrations.requestsWrapper


def proxy_site_spys():
    # https://spys.me/proxy.txt
    proxies_table = automon.integrations.requestsWrapper.RequestsClient('https://spys.me/proxy.txt')
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


def proxy_site_free_proxy_list():
    # https://free-proxy-list.net/
    proxies_table = automon.integrations.requestsWrapper.RequestsClient('https://free-proxy-list.net/')
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


def proxy_get_random_proxy() -> list:
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

    return proxies_master_list


def proxy_filter_https_proxies():
    proxies_master_list = proxy_get_random_proxy()
    return proxies_master_list[proxies_master_list['Https'] == True]


def proxy_filter_https_ips_and_ports():
    proxies_master_list = proxy_filter_https_proxies()
    ips_and_ports = [f'{x}:{y}' for x, y in proxies_master_list[['IP Address', 'Port']].to_records(index=False)]

    return ips_and_ports


def proxy_filter_https_ips_and_ports_get_random():
    return random.choice(proxy_filter_https_ips_and_ports())
