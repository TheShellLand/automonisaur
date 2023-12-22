import scrapy

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class ScrapyClient(object):

    def Selector(self, text: str):
        return scrapy.selector.Selector(text=text)

    def xpath(self, text: str, xpath: str):
        return self.Selector(text=text).xpath(xpath).get()
