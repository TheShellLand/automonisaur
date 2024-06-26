import os
import sys

from bs4 import BeautifulSoup

from automon import log
from automon.helpers import Run
from automon.helpers import Dates

from .ssid import Ssid
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

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


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
        self._airport = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'

        self._connected = None
        self._channel = None
        self._network = None
        self._info = None

        self._runner = Run()

        self.scan_cmd = None
        self.scan_date = None
        self._scan_error = None
        self._scan_output = None

        self.scan_result = ScanXml()

    def __repr__(self):
        return ''

    @staticmethod
    def _command(command: str) -> list:
        return f'{command}'.split(' ')

    async def create_psk(self, ssid: str, passphrase: str):
        """Create PSK from specified pass phrase and SSID."""
        if await self.run(args=f'-P --ssid={ssid} --password={passphrase}'):
            return f'{bytes(self._scan_output).decode()}'.strip()
        return False

    async def disassociate(self):
        """Disassociate from any network."""
        return await self.run(args='-z')

    async def getinfo(self):
        """Print current wireless status, e.g. signal info, BSSID, port type etc."""
        return await self.run(args='-I')

    async def isReady(self):
        if sys.platform == 'darwin':
            if os.path.exists(self._airport):
                logger.debug(f'Airport found! {self._airport}')
                return True
            else:
                logger.error(f'Airport not found! {self._airport}')
        return False

    async def run(self, args: str = None):
        """Run airport"""
        if not await self.isReady():
            return False

        command = f'{self._airport}'

        if args:
            command = f'{self._airport} {args}'

        self.scan_cmd = command
        self.scan_date = Dates.iso()

        try:
            logger.info(command)
            if self._runner.Popen(command=command, text=True):
                self._scan_output = self._runner.stdout
                return True
        except Exception as e:
            logger.error(e)
            raise (Exception(e))

        return False

    async def set_channel(self, channel: int):
        """Set arbitrary channel on the card."""
        return await self.run(args=f'-c {channel}')

    async def scan(self, channel: int = None, args: str = None, ssid: str = None):
        """Perform a wireless broadcast scan."""

        cmd = f'-s'

        if channel is not None:
            cmd = f'{cmd} -c {channel}'

        if ssid is not None:
            cmd = f'{cmd} {ssid}'

        if args:
            cmd = f'{cmd} {args}'

        if await self.run(args=cmd):
            self._scan_output = self._runner.stdout
            self._scan_error = self._runner.stderr
            return True

        return False

    async def scan_channel(self, channel: int = None):
        return await self.scan(channel=channel)

    async def scan_summary(self, channel: int = None, args: str = None, output: bool = True):
        if await self.scan(channel=channel, args=args):
            if output:
                logger.info(f'{self._scan_output}')
            return True
        return False

    @property
    def ssids(self):
        return self.scan_result.ssids

    async def scan_xml(self, ssid: str = None, channel: int = None) -> [Ssid]:
        """Run scan and process xml output."""

        await self.scan(ssid=ssid, args='-x', channel=channel)

        data = self._scan_output
        data = [x for x in data.splitlines()]
        data = [x.decode() for x in data]
        data = [f'{x}' for x in data]
        data = [x.strip() for x in data]
        data = ''.join(data)

        try:
            # root = xmltodict.parse(data)
            # root = pd.read_xml(data)
            # root = ET.fromstring(data)
            # root = etree.fromstring(data.encode())
            root = BeautifulSoup(data, "xml")

            self.scan_result.load_xml(root)

            if self.scan_result.ssids:
                return True

        except Exception as e:
            logger.error(f'Scan not parsed: {e}, {self.scan_cmd}')

        return False
