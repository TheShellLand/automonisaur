from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

caps = DesiredCapabilities.CHROME
 #as per latest docs
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
driver = webdriver.Chrome(desired_capabilities=caps)


class SeleniumDesiredCapabilities(DesiredCapabilities):

    def __init__(self):
        pass

    @property
    def DesiredCapabilities(self):
        return DesiredCapabilities

    @property
    def CHROME(self):
        return self.DesiredCapabilities.CHROME