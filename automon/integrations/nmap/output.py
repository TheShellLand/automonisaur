import mmap
import xmltodict
import pandas as pd

from automon import Logging
from automon.helpers.runner import Run
from automon.helpers.datascience import Pandas


class NmapResult:
    def __init__(self, file: str, run: Run = None, **kwargs):
        self._log = Logging(name=NmapResult.__name__, level=Logging.INFO)

        self.file = file
        self._run = run

        with open(self.file, 'r+') as f:
            mm = mmap.mmap(f.fileno(), 0)
            xml = xmltodict.parse(mm)

        self.df = Pandas().DataFrame(data=xml, **kwargs)

        # normalize output data
        for index in self.df.nmaprun.index:
            try:
                self.df.nmaprun[index] = pd.json_normalize(self.df.nmaprun[index])
                self.df = self.df.combine_first(self.df.nmaprun[index])
                self.df.nmaprun = self.df.drop(index)
                self._log.debug(f'OK normalized {index}')
            except Exception as e:
                self._log.debug(f'not normalized. {index} {type(self.df.nmaprun[index])} {e}')

        if 'ports.port' in self.df:
            ports = pd.json_normalize(self.df['ports.port'].dropna())
            ports = [pd.json_normalize(ports[x]) for x in ports]
            self.df = self.df.drop(columns='ports.port')
            self.df = self.df.combine_first(pd.concat(ports))
            self.ports = self.df.loc[:, ['@portid', 'state.@state', 'state.@reason', '@protocol',
                                         'service.@name', 'status.@reason', 'status.@state']].dropna()
        else:
            self.ports = None

        self.command = self.df.loc['@args'].dropna().iloc[0]
        self.time_start = self.df.loc['@start'].dropna().iloc[0]
        self.time_startstr = self.df.loc['@startstr'].dropna().iloc[0]

        if 'hostnames.hostname.@name' in self.df:
            self.hostnames = self.df['hostnames.hostname.@name'].dropna()
        else:
            self.hostnames = None

        self.hosts_up = self.df['hosts.@up'].dropna().iloc[0]
        self.hosts_down = self.df['hosts.@down'].dropna().iloc[0]
        self.hosts_total = self.df['hosts.@total'].dropna().iloc[0]

        self.version = self.df.loc['@version'].dropna().iloc[0]

        self.elapsed = self.df['finished.@elapsed'].dropna().iloc[0]
        self.summary = self.df['finished.@summary'].dropna().iloc[0]
        self.time_finished = self.df['finished.@time'].dropna().iloc[0]

    def __repr__(self):
        return f'{self.df}'
