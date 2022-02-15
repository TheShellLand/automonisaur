from automon.log import Logging

log = Logging(name='Ssid', level=Logging.DEBUG)


class Ssid:
    def __init__(self, ssid: dict):
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
        self.SSID_B64 = self._ssid.get('SSID', None)
        self.SSID_STR = self._ssid.get('SSID_STR', None)

        # custom
        self.CHANNEL_OFFSET = self.HT_SECONDARY_CHAN_OFFSET
        self.CHANNEL_OFFSET_FULL = f'{self.CHANNEL},+{self.CHANNEL_OFFSET}'
        self.CHANNELS = self.IE_KEY_80211D_NUM_CHANNELS
        self.COUNTRY = self.IE_KEY_80211D_COUNTRY_CODE
        self.DEVICE_INFO = self.INFO
        self.DISTANCE = self.RSSI
        self.MAC = self.BSSID
        self.MAX_POWER = self.IE_KEY_80211D_MAX_POWER
        self.POWER = self.RSSI
        self.SSID = self.SSID_STR
        self.WPS_STATE = self.IE_KEY_WPS_SC_STATE

        log.debug(f'{self.summary}')

    def __repr__(self):
        return f'{self.summary}'

    def __eq__(self, other):
        if isinstance(other, Ssid):
            return self.BSSID == other.BSSID

    def __lt__(self, other):
        if isinstance(other, Ssid):
            return self.RSSI < other.RSSI

    @property
    def summary(self):
        return f'[rssi: {self.DISTANCE} dBm] ' \
               f'{self.SSID} ' \
               f'[ch: {self.CHANNEL}] ' \
               f'[bssid: {self.MAC}] ' \
               f'[noise: {self.NOISE}] ' \
               f'[age: {self.AGE}] '
