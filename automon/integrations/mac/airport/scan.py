from automon.log.logger import Logging
from automon.helpers.dates import Dates

log = Logging(name='Scan', level=Logging.DEBUG)


class Scan:
    def __init__(self, scan: dict, result: dict):
        self._data = result
        self.scan_date = scan['scan_date']

        try:
            self._scans = result['plist']['array']['dict']
            self.ssids = [Ssid(ssid) for ssid in self._scans]
        except Exception as e:
            self.ssids = []
            log.error(f'Scan failed to parse, {" ".join(scan["cmd"])}')

    def __repr__(self):
        return f'{[[x.ssid for x in self.ssids]]}'

    def __eq__(self, other):
        if isinstance(other, Scan):
            return self.ssids == other.ssids


class Ssid:
    def __init__(self, ssid: dict):
        self._ssid = ssid

        self.mac = ssid['string'][0]
        self.ssid = ssid['string'][1]
        self.device_info = self._device_info(ssid) or ''

        log.debug(f'Found SSID: {self.ssid} ({self.mac}) {self.device_info}')

    def _device_info(self, ssid):
        if 'dict' in ssid:
            for key in ssid['dict']:
                if isinstance(key, dict):
                    if 'string' in key.keys() and 'data' in key.keys() and 'dict' in key.keys():
                        if isinstance(key['string'], list):
                            return key['string']

    def __repr__(self):
        return f'{self.ssid} {self.mac} {self.device_info}'

    def __eq__(self, other):
        if isinstance(other, Ssid):
            return self.mac, self.ssid == other.mac, other.ssid

    def __lt__(self, other):
        if isinstance(other, Ssid):
            return self.ssid == other.ssid
