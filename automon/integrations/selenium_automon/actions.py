from selenium.webdriver.common.action_chains import ActionChains

from automon.log import Logging

log = Logging(name='selenium', level=Logging.INFO)


class SeleniumActions:
    @staticmethod
    def click(browser, xpath):
        """Given an xpath, it will click it

        :param browser: selenium browser
        :param xpath: chrome xpath
        :return:
        """
        element = browser.find_element_by_xpath(xpath)
        return element.click()

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
