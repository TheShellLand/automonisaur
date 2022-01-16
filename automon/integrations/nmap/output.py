import mmap
import xmltodict
import pandas as pd

from automon.log import Logging
from pandas import DataFrame
from automon.helpers.runner import Run
from automon.integrations.datascience import Pandas


class NmapResult(object):
    def __init__(self, file: str = None, run: Run = None, **kwargs):
        self._log = Logging(name=NmapResult.__name__, level=Logging.INFO)

        self.file = file
        self._run = run

        if file:

            with open(self.file, 'r+') as f:
                mm = mmap.mmap(f.fileno(), 0)
                xml = xmltodict.parse(mm)

            self.df = Pandas().DataFrame(data=xml, **kwargs)

            df = Pandas().DataFrame(data=xml, **kwargs)

            if 'host' in df.nmaprun:
                self.host = self._normalize_ports(df)
            else:
                self.host = None

            if 'hosthint' in df.nmaprun:
                self._hosthint = pd.json_normalize(df.loc['hosthint'])
            else:
                self._hosthint = None

            self._runstats = pd.json_normalize(df.loc['runstats'])
            self._scaninfo = pd.json_normalize(df.loc['scaninfo'])
            self._verbose = pd.json_normalize(df.loc['verbose'])

            # normalize output data

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

            self._log.info(f'hosts up: {self.hosts_up}')
            self._log.info(f'hosts down: {self.hosts_down}')
            # self._log.info(f'hosts total: {self.hosts_total}')
            self._log.info(f'{self.summary}')
            self._log.info(f'finished processing output ({round(df.memory_usage().sum() / 1024, 2)} Kb)')

    def ports(self, df: DataFrame = None):
        if df:
            return self._get_ports(df)
        return self._get_ports()

    def _get_ports(self, df: DataFrame = None) -> DataFrame or False:

        if df is None:
            if self.host is not None:
                df_host = self.host
        else:
            df_host = pd.json_normalize(df.nmaprun.loc['host'])

        if 'ports.port' in df_host:
            s_ports = df_host.loc[:, 'ports.port']
            s_ports = s_ports.apply(lambda _list: pd.json_normalize(_list))
            return s_ports

        return False

    def _normalize_ports(self, df):

        df_host = pd.json_normalize(df.nmaprun.loc['host'])

        if 'ports.port' in df_host:
            s_ports = df_host.loc[:, 'ports.port']
            s_ports = s_ports.apply(lambda _list: pd.json_normalize(_list))
            scanned_ports = s_ports.apply(lambda x: x.loc[:, '@portid'])
            scanned_ports = scanned_ports.iloc[0].to_list()

            i = 0
            while i < s_ports.size:
                # get series index
                # use index to save port result to
                s_result = s_ports.iloc[i]

                for port in scanned_ports:
                    _row = s_result[s_result.loc[:, '@portid'] == port]
                    status = _row.loc[:, 'state.@state']
                    status.index = [i]

                    if port not in df_host:
                        df_host[port] = status
                    else:
                        df_host[port].update(status)

                    self._log.debug(f"{df_host.loc[:, ['address.@addr'] + [x for x in scanned_ports if x in df_host]]}")

                i += 1

            return df_host

    def hostnames(self):
        if 'hostnames.hostname.@name' in self.host:
            return self.host.loc[:, 'hostnames.hostname.@name']
        return False

    def ips(self):
        if 'address.@addr' in self.host:
            return self.host.loc[:, 'address.@addr']
        return False

    def __repr__(self):
        msg = f'{self.summary} '

        if self.df.memory_usage().sum() / 1024 / 1024 / 1024 > 1:
            msg += f'({round(self.df.memory_usage().sum() / 1024 / 1024 / 1024, 2)} Gb)'
        else:
            msg += f'({round(self.df.memory_usage().sum() / 1024, 2)} Kb)'

        return msg

    def __len__(self):
        return int(self.df.memory_usage().sum())
