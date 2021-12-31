from automon.log import Logging

log = Logging(name=__name__, level=Logging.DEBUG)


class Scan:
    def __init__(self, scan: dict, result: dict):
        self._log = Logging(name=Scan.__name__, level=Logging.DEBUG)
        self._data = result
        self.scan_date = scan['scan_date']
        self.ssids = []

        try:
            self._scans = result['plist']['array']['dict']
        except Exception as e:
            self.ssids = []
            self._log.debug(f'No ssids found, {" ".join(scan["cmd"])}')

        self.ssids = [Ssid(ssid) for ssid in self._scans]

        self.summary = {}

        for ssid in self.ssids:
            s_ssid = ssid.ssid
            self.summary[s_ssid] = 0

        for ssid in self.ssids:
            s_ssid = ssid.ssid
            s_mac = ssid.mac
            s_device = ssid.device_info

            self.summary[s_ssid] += 1

        sort = sorted(self.summary.items(), key=lambda kv: kv[1], reverse=True)

        [self._log.debug(f'{k}: {v}')
         for k, v in sort]

        self._log.debug(f'Total SSIDs: {len(self.ssids)}')

    def __repr__(self):
        return f'{[[x.ssid for x in self.ssids]]}'

    def __eq__(self, other):
        if isinstance(other, Scan):
            return self.ssids == other.ssids


class Ssid:
    def __init__(self, ssid: dict):
        self._log = Logging(name=Ssid.__name__, level=Logging.DEBUG)
        self._ssid = ssid

        self.mac = ssid['string'][0]
        self.ssid = ssid['string'][1]
        self.device_info = self._device_info(ssid) or ''

        log.debug(f'Found SSID: {self.ssid} ({self.mac}) {self.device_info}')

    @staticmethod
    def _device_info(ssid):
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
            return self.mac == other.mac

    def __lt__(self, other):
        if isinstance(other, Ssid):
            return self.ssid < other.ssid
