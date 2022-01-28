from automon.log import Logging


class Ssid:
    def __init__(self, ssid: dict):
        self._log = Logging(name=Ssid.__name__, level=Logging.DEBUG)
        self._ssid = ssid

        self.mac = ssid['string'][0]
        self.ssid = ssid['string'][1]
        self.device_info = self._device_info(ssid) or ''

        self._log.debug(f'Found SSID: {self.ssid} ({self.mac}) {self.device_info}')

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
