import random

from automon.log import logger

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class SeleniumUserAgentBuilder:
    googlebot = [
        'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36',
    ]

    top = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    ]

    macox = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13.3; rv:112.0) Gecko/20100101 Firefox/112.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Vivaldi/5.7.2921.68',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48',
    ]
    windows = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Vivaldi/5.7.2921.68',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Vivaldi/5.7.2921.68',
    ]

    agents = [

    ]
    agents.extend(googlebot)
    agents.extend(top)
    agents.extend(macox)
    agents.extend(windows)

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
