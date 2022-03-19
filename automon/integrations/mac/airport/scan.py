from bs4 import BeautifulSoup

from automon.log import Logging

from .ssid import Ssid

log = Logging(name='ScanXml', level=Logging.DEBUG)


class ScanXml:
    def __init__(self, xml: BeautifulSoup = None):
        self._xml = xml

    def __repr__(self):
        return f'{self.summary}'

    def __eq__(self, other):
        if isinstance(other, ScanXml):
            return self._xml == other._xml

    def _bs2dict(self, bs: BeautifulSoup, **kwargs):
        d = {}

        key = None
        value = None

        if 'key' in kwargs:
            key = kwargs['key']

        if 'value' in kwargs:
            value = kwargs['value']

        if hasattr(bs, 'contents'):
            d.update(self._bs2dict(bs.contents, key=key, value=bs.contents))

        elif isinstance(bs, list):
            for tag in bs:
                if tag.name == 'key':
                    key = tag.text
                d.update(self._bs2dict(tag, key=key, value=tag))

        elif key and value:
            d.update({key: value})

        else:
            if '_missed' in d.keys():
                d['_missed'].append({key: value})
            else:
                d['_missed'] = [{key: value}]

        return d

    def byAge(self):
        return sorted(self.ssids, key=(lambda x: x.AGE))

    def byDistance(self):
        return sorted(self.ssids, key=(lambda x: x.RSSI), reverse=True)

    def bySsid(self):
        return sorted(self.ssids, key=(lambda x: x.SSID))

    def load_xml(self, xml: BeautifulSoup):
        self._xml = xml

    @property
    def ssids(self) -> [Ssid]:
        """list of Ssid sorted by closest distance"""

        xml = self._xml
        scan = None
        ssids = None

        try:
            bssids = xml.contents[1].contents[0].contents
            scan = [self._bs2dict(x) for x in bssids]
        except:
            log.error(f'No BSSIDs', enable_traceback=False)

        if scan:
            ssids = [Ssid(ssid) for ssid in scan]
            ssids = sorted(ssids, reverse=True)

        return ssids

    @property
    def summary(self) -> dict:
        summary = {}

        if not self.ssids:
            return f'no ssids'

        ssids = self.ssids
        summary['Total SSID'] = len(ssids)

        if len(ssids) < 0:
            return summary

        summary['SSID'] = {}

        for ssid in ssids:
            count = summary['SSID'].get(ssid.SSID, 0) + 1
            summary['SSID'][ssid.SSID] = count
        summary['SSID'] = {k: v for k, v in sorted(summary['SSID'].items())}

        log.info(f'Total SSID: {summary["Total SSID"]}')
        return summary
