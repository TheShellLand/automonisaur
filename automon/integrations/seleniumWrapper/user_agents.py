import io
import random
import pandas

import automon.integrations.requestsWrapper

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


def site_useragents():
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

    agents = []

    agents.extend(googlebot)
    agents.extend(site_useragents()['desktop_most_common_useragents']['useragent'].tolist())

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

    def get_random_agent(self, filter: list or str = None, **kwargs):
        if filter:
            filtered_agents = self.filter_agent(filter, **kwargs)
            if filtered_agents:
                return random.choice(filtered_agents)
            else:
                return ''

        return random.choice(self.agents)

    def pick_random(self, choices: list):
        return random.choice(choices)

    def get_mac(self, **kwargs):
        return self.get_random_agent(filter='Macintosh', **kwargs)

    def get_top(self, **kwargs):
        return self.pick_random(self.top)

    def get_windows(self, **kwargs):
        return self.get_random_agent(filter='Windows', **kwargs)
