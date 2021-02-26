import xmltodict
import subprocess

from queue import Queue
from subprocess import PIPE

from automon.log.logger import Logging
from automon.helpers.dates import Dates
from automon.integrations.mac.airport.scan import Scan

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


        # makbuk: eric$ /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport  -h
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

        self.scans = []
        self.parsed_scans = []
        self.ssids = []

        self._queue = Queue()

    def __repr__(self):
        return ''

    def _command(self, command: str) -> list:
        return f'{command}'.split(' ')

    def run(self, args=''):
        command = self._command(f'{self._airport} {args}')

        call = subprocess.Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
        output, errors = call.communicate()
        call.wait()

        result = {
            'scan_date': Dates.iso,
            'cmd': command,
            'output': output,
            'errors': errors
        }

        return result

    def scan(self, channel: int = None, args: str = ''):
        if channel:
            result = self.run(args=f'-s{channel} {args}')
        else:
            result = self.run(args=f'-s {args}')

        self.scans.append(result)

        return result

    def scan_summary(self, channel: int = None, args: str = '', output: bool = True):
        if channel is not None:
            res = self.scan(channel=channel, args=args)
        else:
            res = self.scan(args=args)

        self._log.debug(f'Channel: {channel}')

        if output:
            print(f"{res['output']}")

        return res

    def set_channel(self, channel: int):
        return self.run(args=f'-c{channel}')

    def getinfo(self):
        return self.run(args='-I')

    def disassociate(self, network: str):
        return self.run(args='-z')

    def create_psk(self, ssid: str, passphrase: str):
        return self.run(args=f'-P --ssid={ssid} --password={passphrase}')['output']

    def scan_xml(self, channel: int = None):
        if channel is not None:
            scan = self.scan(args='-x', channel=channel)
        else:
            scan = self.scan(args='-x')

        data = scan['output']
        data = [x.strip() for x in data.splitlines()]
        data = ''.join(data)

        root = xmltodict.parse(data)

        parsed = Scan(scan=scan, result=root)
        self.parsed_scans.append(parsed)

        for ssid in parsed.ssids:
            self._queue.put(ssid)
            self.ssids.append(ssid)

        return parsed