import mmap
import xmltodict
import pandas as pd

from automon import Logging
from automon.helpers.runner import Run
from automon.helpers.datascience import Pandas


class NmapResult(object):
    def __init__(self, file: str, run: Run = None, **kwargs):
        self._log = Logging(name=NmapResult.__name__, level=Logging.INFO)

        self.file = file
        self._run = run

        with open(self.file, 'r+') as f:
            mm = mmap.mmap(f.fileno(), 0)
            xml = xmltodict.parse(mm)

        self.df = Pandas().DataFrame(data=xml, **kwargs)

        df = Pandas().DataFrame(data=xml, **kwargs)

        self.host = pd.json_normalize(df.loc['host'][0])
        self._hosthint = pd.json_normalize(df.loc['hosthint'])
        self._runstats = pd.json_normalize(df.loc['runstats'])
        self._scaninfo = pd.json_normalize(df.loc['scaninfo'])
        self._verbose = pd.json_normalize(df.loc['verbose'])

        # normalize output data
        # TODO: missing both ports, only shows one port?
        if 'ports.port' in self.host:
            ports = self.host.loc[:, 'ports.port'].apply(
                lambda _list: _list[0]).apply(
                lambda _dict: pd.json_normalize(_dict).to_dict())
            ports = pd.json_normalize(ports)
            self.host = self.host.combine_first(ports)
            self.host = self.host.drop(columns='ports.port')

        self.command = df.loc['@args'][0]
        self.cmd = self.command
        self.time_start = df.loc['@start'][0]
        self.time_startstr = df.loc['@startstr'][0]

        self.hosts_up = self._runstats.loc[:, 'hosts.@up'][0]
        self.hosts_down = self._runstats.loc[:, 'hosts.@down'][0]
        self.hosts_total = self._runstats.loc[:, 'hosts.@total'][0]

        self.version = df.loc['@version'].iloc[0]

        self.elapsed = self._runstats.loc[:, 'finished.@elapsed'][0]
        self.summary = self._runstats.loc[:, 'finished.@summary'][0]
        self.time_finished = self._runstats.loc[:, 'finished.@time'][0]

    def hostnames(self):
        return self.host.loc[:, 'hostnames.hostname.@name']

    def ips(self):
        return self.host.loc[:, 'address.@addr']

    def __repr__(self):
        msg = f'up: {self.hosts_up} ' \
              f'down: {self.hosts_down} ' \
              f'total: {self.hosts_total} ' \
              f'elapsed: {self.elapsed} ' \
              f'summary: {self.summary} ' \
              f'cmd: {self.command} ' \
              f''

        if self.df.memory_usage().sum() / 1024 / 1024 / 1024 > 1:
            msg += f'{round(self.df.memory_usage().sum() / 1024 / 1024 / 1024, 2)} Gb'
        else:
            msg += f'{round(self.df.memory_usage().sum() / 1024, 2)} Kb'

        return msg

    def __len__(self):
        return int(self.df.memory_usage().sum())
