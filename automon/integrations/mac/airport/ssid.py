import collections

from automon.log import Logging


class Ssid:
    def __init__(self, ssid: dict):
        self._log = Logging(name=Ssid.__name__, level=Logging.DEBUG)
        self._ssid = dict(sorted(ssid.items()))

        self.AGE = int(self._ssid.get('AGE', 0))
        self.AP_MODE = self._ssid.get('AP_MODE', None)
        self.BSSID = f"{self._ssid.get('BSSID', None)}".upper()
        self.CHANNEL = self._ssid.get('CHANNEL', None)
        self.HT_SECONDARY_CHAN_OFFSET = self._ssid.get('HT_SECONDARY_CHAN_OFFSET', None)
        self.INFO = self._ssid.get('INFO', None)
        self.IE_KEY_80211D_COUNTRY_CODE = self._ssid.get('IE_KEY_80211D_COUNTRY_CODE', None)
        self.IE_KEY_80211D_MAX_POWER = self._ssid.get('IE_KEY_80211D_MAX_POWER', None)
        self.IE_KEY_80211D_NUM_CHANNELS = self._ssid.get('IE_KEY_80211D_NUM_CHANNELS', None)
        self.IE_KEY_WPS_SC_STATE = self._ssid.get('IE_KEY_WPS_SC_STATE', None)
        self.NOISE = int(self._ssid.get('NOISE', 0))
        self.RATES = self._ssid.get('RATES', None)
        self.RSSI = int(self._ssid.get('RSSI', 0))
        self.SSID = self._ssid.get('SSID', None)
        self.SSID_STR = self._ssid.get('SSID_STR', None)

        self.age = self.AGE
        self.ap_mode = self.AP_MODE
        self.bssid = self.BSSID
        self.channel = self.CHANNEL
        self.channel_offset = self.HT_SECONDARY_CHAN_OFFSET
        self.channel_offset_full = f'{self.channel},+{self.channel_offset}'
        self.channels = self.IE_KEY_80211D_NUM_CHANNELS
        self.country = self.IE_KEY_80211D_COUNTRY_CODE
        self.device_info = self.INFO
        self.distance = self.RSSI
        self.mac = self.BSSID
        self.max_power = self.IE_KEY_80211D_MAX_POWER
        self.noise = self.NOISE
        self.power = self.RSSI
        self.rates = self.RATES
        self.rssi = self.RSSI
        self.ssid = self.SSID_STR
        self.wps_state = self.IE_KEY_WPS_SC_STATE

        self.summary = f'[rssi: {self.distance}] ' \
                       f'[ch: {self.channel}] ' \
                       f'{self.ssid} ' \
                       f'[bssid: {self.mac}] ' \
                       f'[noise: {self.noise}] ' \
                       f'[age: {self.age}] '

        self._log.debug(f'{self.summary}')

    def __repr__(self):
        return f'{self.summary}'

    def __eq__(self, other):
        if isinstance(other, Ssid):
            return self.bssid == other.bssid

    def __lt__(self, other):
        if isinstance(other, Ssid):
            return self.rssi < other.rssi
