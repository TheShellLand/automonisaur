import scrapy

from automon.log import Logging

log = Logging(name='ScrapyClient', level=Logging.DEBUG)


class ScrapyClient(object):

    def Selector(self, text: str):
        return scrapy.selector.Selector(text=text)

    def xpath(self, text: str, xpath: str):
        return self.Selector(text=text).xpath(xpath).get()
