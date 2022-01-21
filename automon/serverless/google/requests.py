import io
import flask

from flask.wrappers import Request

from automon import Logging
from automon.integrations.datascience import Pandas


class Requests(object):
    log = Logging(name=__name__, level=Logging.INFO)

    def __init__(self, requests: flask.wrappers.Request = None):
        self.requests = requests
        self._pandas = Pandas()

        if self.requests:
            self.log.debug(self)

    def __repr__(self):
        return f'{self.__dict__}'

    def toJson(self) -> bytes:
        csv = self.toCsv()
        df = self._pandas.read_csv(csv)

        json_ = df.to_json(orient='records')
        json_ = f'{json_}'.encode()

        self.log.info(f'JSON size: {len(json_)} B')
        self.log.debug(json_)
        return json_

    def toCsv(self) -> io.StringIO:
        df = self.request2df()
        csv = df.to_csv(index=False)
        csv_s = io.StringIO(csv)
        self.log.info(f'CSV size: {len(csv)} B')
        self.log.debug(csv)
        return csv_s

    def request2df(self) -> Pandas.DataFrame:
        return self.toDataFrame()

    def toSeries(self) -> Pandas.Series:
        r = self.requests
        r = r.__dict__
        s = self._pandas.Series(r)
        self.log.debug(s)
        return s

    def toDataFrame(self) -> Pandas.DataFrame:
        s = self.toSeries()
        d = self._pandas.DataFrame(s).T
        self.log.debug(d)
        return d

    def toDict(self, data: str = None) -> dict:
        return dict(data=data)
