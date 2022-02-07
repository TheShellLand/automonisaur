from bs4 import BeautifulSoup

from automon import Logging

from .ssid import Ssid


class ScanXml:
    def __init__(self, result: BeautifulSoup):
        self._log = Logging(name=ScanXml.__name__, level=Logging.DEBUG)
        self._result = result
        self._scans = []

        self.ssids = []
        self.summary = {}

        try:
            _bssids = result.contents[1].contents[0].contents
            self._scans = [self._bs2dict(x) for x in _bssids]
        except Exception as e:
            self._log.error(f'No BSSIDs', enable_traceback=False)

        self.ssids = sorted([Ssid(_ssid) for _ssid in self._scans], reverse=True)
        self.summary['Total SSID'] = len(self.ssids)
        self.summary['SSID'] = {}

        for _ssid in self.ssids:
            count = self.summary['SSID'].get(_ssid.ssid, 0) + 1
            self.summary['SSID'][_ssid.ssid] = count
        self.summary['SSID'] = {k: v for k, v in sorted(self.summary['SSID'].items())}

        self._log.info(f'Total SSID: {self.summary["Total SSID"]}')
        # self._log.debug(f'Command: {self._scan_cmd}')

    def __repr__(self):
        return f'{self.summary}'

    def __eq__(self, other):
        if isinstance(other, ScanXml):
            return self.ssids == other.ssids

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
        self.ssids = sorted(self.ssids, key=(lambda x: x.age))
        return self.ssids

    def byDistance(self):
        self.ssids = sorted(self.ssids, key=(lambda x: x.rssi), reverse=True)
        return self.ssids

    def bySsid(self):
        self.ssids = sorted(self.ssids, key=(lambda x: x.ssid))
        return self.ssids
