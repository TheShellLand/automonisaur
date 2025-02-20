import io
import random
import pandas

import automon.integrations.requestsWrapper

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


def public_site_useragents():
    url = 'https://www.useragents.me/'
    proxies_table = automon.integrations.requestsWrapper.RequestsClient(url)
    proxies_table.get()

    proxies_tables = pandas.read_html(io.StringIO(proxies_table.text))

    # Most Common Desktop Useragents
    desktop_most_common_useragents = proxies_tables[0]

    # Most Common Mobile Useragents
    mobile_most_common_useragents = proxies_tables[1]

    # Latest Windows Desktop Useragents
    desktop_latest_windows_useragents = proxies_tables[2]

    # Latest Mac OS X Desktop Useragents
    desktop_latest_macosx_useragents = proxies_tables[3]

    # Latest Linux Desktop Useragents
    desktop_latest_linux_useragents = proxies_tables[4]

    # Latest iPhone Useragents
    mobile_latest_iphone_useragents = proxies_tables[5]

    # Latest iPod Useragents
    ipod_latest_useragents = proxies_tables[6]

    # Latest iPad Useragents
    ipad_latest_useragents = proxies_tables[7]

    # Latest Android Mobile Useragents
    mobile_latest_android_useragents = proxies_tables[8]

    # Latest Tablet Useragents
    tablet_latest_useragents = proxies_tables[9]

    return dict(
        desktop_most_common_useragents=desktop_most_common_useragents,
        mobile_most_common_useragents=mobile_most_common_useragents,
        desktop_latest_windows_useragents=desktop_latest_windows_useragents,
        desktop_latest_macosx_useragents=desktop_latest_macosx_useragents,
        desktop_latest_linux_useragents=desktop_latest_linux_useragents,
        mobile_latest_iphone_useragents=mobile_latest_iphone_useragents,
        ipod_latest_useragents=ipod_latest_useragents,
        ipad_latest_useragents=ipad_latest_useragents,
        mobile_latest_android_useragents=mobile_latest_android_useragents,
        tablet_latest_useragents=tablet_latest_useragents,
    )


class SeleniumUserAgentBuilder:
    googlebot = [
        'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36',
    ]

    desktop_most_common_useragents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.',
        'Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/115.',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/95.0.0.',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.3'
    ]

    desktop_latest_linux_useragents = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux i686; rv:134.0) Gecko/20100101 Firefox/134.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:134.0) Gecko/20100101 Firefox/134.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0',
        'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0',
        'Mozilla/5.0 (X11; Linux i686; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/116.0.0.0'
    ]

    desktop_latest_macosx_useragents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/131.0.2903.86',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:134.0) Gecko/20100101 Firefox/134.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/116.0.0.0'
    ]

    desktop_latest_windows_useragents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/131.0.2903.86',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox One) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edge/44.18363.8131',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/116.0.0.0',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/116.0.0.0'
    ]

    mobile_most_common_useragents = [
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.3',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/27.0 Chrome/125.0.0.0 Mobile Safari/537.3',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/353.1.720279278 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (Linux; Android 10; moto e(6i) Build/QOH30.280-26) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.163 Mobile Safari/537.3',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/132.0.6834.100 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/132.0.6834.100 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/132.0.6834.100 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.3',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/132.0.6834.100 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/133.0.6943.33 Mobile/15E148 Safari/604.',
        'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36 (compatible; Google-Read-Aloud; +https://support.google.com/webmasters/answer/1061943',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/133.0.6943.33 Mobile/15E148 Safari/604.'
    ]
    mobile_latest_android_useragents = [
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.164 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; HD1913) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.164 Mobile Safari/537.36 EdgA/131.0.2903.87',
        'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.164 Mobile Safari/537.36 EdgA/131.0.2903.87',
        'Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.164 Mobile Safari/537.36 EdgA/131.0.2903.87',
        'Mozilla/5.0 (Linux; Android 10; ONEPLUS A6003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.164 Mobile Safari/537.36 EdgA/131.0.2903.87',
        'Mozilla/5.0 (Windows Mobile 10; Android 10.0; Microsoft; Lumia 950XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36 Edge/40.15254.603',
        'Mozilla/5.0 (Android 15; Mobile; rv:134.0) Gecko/134.0 Firefox/134.0',
        'Mozilla/5.0 (Android 15; Mobile; LG-M255; rv:134.0) Gecko/134.0 Firefox/134.0',
        'Mozilla/5.0 (Linux; Android 10; VOG-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.164 Mobile Safari/537.36 OPR/76.2.4027.73374',
        'Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.164 Mobile Safari/537.36 OPR/76.2.4027.73374',
        'Mozilla/5.0 (Linux; Android 10; SM-N975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.164 Mobile Safari/537.36 OPR/76.2.4027.73374'
    ]

    mobile_latest_iphone_useragents = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/133.0.6943.33 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 EdgiOS/131.2903.92 Mobile/15E148 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/135.0 Mobile/15E148 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1'
    ]

    ipad_latest_useragents = [
        'Mozilla/5.0 (iPad; CPU OS 14_7_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/135.0 Mobile/15E148 Safari/605.1.15',
        'Mozilla/5.0 (iPad; CPU OS 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1'
    ]

    ipod_latest_useragents = [
        'Mozilla/5.0 (iPod; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/133.0.6943.33 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPod touch; CPU iPhone OS 14_7_3 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) FxiOS/135.0 Mobile/15E148 Safari/605.1.15',
        'Mozilla/5.0 (iPod touch; CPU iPhone 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1'
    ]

    tablet_latest_useragents = []

    agents = []

    agents.extend(desktop_most_common_useragents)
    agents.extend(desktop_latest_windows_useragents)
    agents.extend(desktop_latest_macosx_useragents)
    agents.extend(desktop_latest_linux_useragents)
    agents.extend(mobile_most_common_useragents)
    agents.extend(mobile_latest_iphone_useragents)
    agents.extend(mobile_latest_iphone_useragents)
    agents.extend(mobile_latest_android_useragents)
    agents.extend(ipod_latest_useragents)
    agents.extend(ipad_latest_useragents)
    agents.extend(tablet_latest_useragents)
    agents.extend(googlebot)

    public_agents = None

    def filter_agent(self, filter: list or str, case_sensitive: bool = False) -> list:
        if isinstance(filter, str):
            filter = [filter]

        filtered_agents = []
        for agent in self.agents:
            if not case_sensitive:
                if any(substring.lower() in agent.lower() for substring in filter):
                    filtered_agents.append(agent)
            else:
                if any(substring in agent for substring in filter):
                    filtered_agents.append(agent)

        return filtered_agents

    def get_bot(self):
        return self.pick_random(self.googlebot)

    def get_top(self):
        return self.pick_random(self.desktop_most_common_useragents)

    def get_mac(self, **kwargs):
        return self.pick_random(self.desktop_latest_macosx_useragents)

    def get_windows(self, **kwargs):
        return self.pick_random(self.desktop_latest_windows_useragents)

    def get_mobile(self, **kwargs):
        return self.pick_random(
            self.mobile_most_common_useragents +
            self.mobile_latest_iphone_useragents +
            self.mobile_latest_iphone_useragents +
            self.mobile_latest_android_useragents
        )

    def pick_random(self, choices: list = None):

        if not choices:
            choices = self.agents

        return random.choice(choices)

    def pick_random_public(self, useragent_type: str = 'desktop-common'):
        """

        """
        if not self.public_agents:
            self.public_agents = public_site_useragents()

        if useragent_type == 'desktop-common':
            return self.public_agents['desktop_most_common_useragents'].sample()['useragent'].item()

        if useragent_type == 'mobile-common':
            return self.public_agents['mobile_most_common_useragents'].sample()['useragent'].item()

        if useragent_type == 'windows-latest':
            return self.public_agents['desktop_latest_windows_useragents'].sample()['useragent'].item()

        if useragent_type == 'macosx-latest':
            return self.public_agents['desktop_latest_macosx_useragents'].sample()['useragent'].item()

        if useragent_type == 'linux-latest':
            return self.public_agents['desktop_latest_linux_useragents'].sample()['useragent'].item()

        if useragent_type == 'iphone':
            return self.public_agents['mobile_latest_iphone_useragents'].sample()['useragent'].item()

        if useragent_type == 'ipod':
            return self.public_agents['ipod_latest_useragents'].sample()['useragent'].item()

        if useragent_type == 'ipad':
            return self.public_agents['ipad_latest_useragents'].sample()['useragent'].item()

        if useragent_type == 'android':
            return self.public_agents['mobile_latest_android_useragents'].sample()['useragent'].item()

        if useragent_type == 'tablet':
            return self.public_agents['tablet_latest_useragents'].sample()['useragent'].item()

        raise Exception(f'[SeleniumUserAgentBuilder] :: ERROR :: useragent_type not found :: {useragent_type=}')
