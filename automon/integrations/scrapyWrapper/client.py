import scrapy

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class ScrapyClient(object):

    def Selector(self, text: str):
        return scrapy.selector.Selector(text=text)

    def xpath(self, text: str, xpath: str):
        return self.Selector(text=text).xpath(xpath).get()
