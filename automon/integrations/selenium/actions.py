from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from automon.log.logger import Logging
from automon.integrations.selenium.config import SeleniumConfig

log = Logging(name='actions', level=Logging.DEBUG)


class SeleniumActions:
    @staticmethod
    def click(browser: SeleniumConfig().webdriver.Chrome, xpath: str, wait: bool):
        """Given an xpath, it will click it

        :param browser: selenium browser
        :param xpath: chrome xpath
        :return:
        """
        while True:
            try:
                if xpath:
                    element = browser.find_element_by_xpath(xpath)
                element.click()
                break
            except:
                log.debug(f'Waiting for element {xpath}')
                if not wait:
                    break

        return True

    @staticmethod
    def type(browser, keys):
        """Given a browser and a list of keys to perform

        :param browser: browser
        :param keys: list of keys
        :return: perform list of keys
        """
        actions = ActionChains(browser)
        for key in keys:
            actions.send_keys(key)

        return actions.perform()
