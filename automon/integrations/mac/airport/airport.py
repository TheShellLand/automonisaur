import os
import sys

from bs4 import BeautifulSoup

from automon import Logging
from automon.helpers import Run
from automon.helpers import Dates

from .scan import ScanXml

flags = {
    '-s': 'scan for wireless networks',
    '-c': '--channel=[<arg>]    Set arbitrary channel on the card',
    '-I': '--getinfo            Print current wireless status, e.g. signal info, BSSID, port type etc.',
    '-z': '--disassociate       Disassociate from any network',
    '-s': '--scan=[<arg>]       Perform a wireless broadcast scan. Will perform a directed scan if the optional <arg> is provided',
    '-x': '--xml                Print info as XML',
    '-P': '--psk                Create PSK from specified pass phrase and SSID.',

}


class Airport:
    def __init__(self):
        """Apple Airport Wi-Fi Utility

        A long hidden airport command line utility buried deep in Mac OS X can be used to scan for and find
        available wireless networks. This powerful tool is very helpful for network admins and systems
        administrators, but it’s handy for the average user to help discover nearby wi-fi routers as well.

        Tested on:
          - Apple M1


        # makbuk: eric$ /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -h
        # Supported arguments:
        #  -c[<arg>] --channel=[<arg>]    Set arbitrary channel on the card
        #  -z        --disassociate       Disassociate from any network
        #  -I        --getinfo            Print current wireless status, e.g. signal info, BSSID, port type etc.
        #  -s[<arg>] --scan=[<arg>]       Perform a wireless broadcast scan.
        # 				   Will perform a directed scan if the optional <arg> is provided
        #  -x        --xml                Print info as XML
        #  -P        --psk                Create PSK from specified pass phrase and SSID.
        # 				   The following additional arguments must be specified with this command:
        #                                   --password=<arg>  Specify a WPA password
        #                                   --ssid=<arg>      Specify SSID when creating a PSK
        #  -h        --help               Show this help
         """

        self._log = Logging(name=Airport.__name__, level=Logging.DEBUG)

        self._airport = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'

        self._connected = None
        self._channel = None
        self._network = None
        self._info = None

        self._runner = Run()

        self.is_mac = False
        self.is_ready = False

        self.scan_cmd = None
        self.scan_date = None
        self.scan_error = None
        self.scan_output = None
        self.scan_result = None

        self.ssids = []

        if os.path.exists(self._airport):
            self.is_ready = True
            self._log.debug(f'Found airport: ({self._airport}')
        else:
            self._log.warn(f'Missing airport program! ({self._airport})')

        if sys.platform == 'darwin':
            self.is_mac = True
            self._log.info(f'Platform is mac: ({sys.platform})')
        else:
            self._log.warn(f'Platform is not a Mac! ({sys.platform})')

    def __repr__(self):
        return ''

    @staticmethod
    def _command(command: str) -> list:
        return f'{command}'.split(' ')

    def create_psk(self, ssid: str, passphrase: str):
        """Create PSK from specified pass phrase and SSID."""
        if self.run(args=f'-P --ssid={ssid} --password={passphrase}'):
            return f'{self.scan_output}'.strip()
        return False

    def disassociate(self):
        """Disassociate from any network."""
        return self.run(args='-z')

    def getinfo(self):
        """Print current wireless status, e.g. signal info, BSSID, port type etc."""
        return self.run(args='-I')

    def run(self, args: str = None):
        """Run airport"""
        if not self.is_ready:
            return False

        command = f'{self._airport}'

        if args:
            command = f'{self._airport} {args}'

        self.scan_cmd = command
        self.scan_date = Dates.iso()

        try:
            self._log.info(command)
            if self._runner.Popen(command=command, text=True):
                self.scan_output = self._runner.stdout
                return True
        except Exception as e:
            self._log.error(e, raise_exception=True)

        return False

    def set_channel(self, channel: int):
        """Set arbitrary channel on the card."""
        return self.run(args=f'-c {channel}')

    def scan(self, channel: int = None, args: str = None, ssid: str = None):
        """Perform a wireless broadcast scan."""

        cmd = f'-s'

        if channel is not None:
            cmd = f'{cmd} -c {channel}'

        if ssid is not None:
            cmd = f'{cmd} {ssid}'

        if args:
            cmd = f'{cmd} {args}'

        if self.run(args=cmd):
            self.scan_output = self._runner.stdout
            self.scan_error = self._runner.stderr
            return True

        return False

    def scan_channel(self, channel: int = None):
        return self.scan(channel=channel)

    def scan_summary(self, channel: int = None, args: str = None, output: bool = True):
        if self.scan(channel=channel, args=args):
            if output:
                self._log.info(f'{self.scan_output}')
            return True
        return False

    def scan_xml(self, ssid: str = None, channel: int = None):
        """Run scan and process xml output."""

        self.scan(ssid=ssid, args='-x', channel=channel)

        data = self.scan_output
        data = [x.strip() for x in data.splitlines()]
        data = ''.join(data)

        try:
            # root = xmltodict.parse(data)
            # root = pd.read_xml(data)
            # root = ET.fromstring(data)
            # root = etree.fromstring(data.encode())
            root = BeautifulSoup(data, "xml")

            self.scan_result = ScanXml(root)
            self.ssids = self.scan_result.ssids

            return True
        except Exception as e:
            self._log.error(f'Scan not parsed: {e}, {self.scan["cmd"]}', enable_traceback=False)

        return False
