from automon.log import Logging

from .ssid import Ssid


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

        self._log.debug(f'Total SSID: {len(self.ssids)}')

    def __repr__(self):
        return f'{[[x.ssid for x in self.ssids]]}'

    def __eq__(self, other):
        if isinstance(other, Scan):
            return self.ssids == other.ssids
