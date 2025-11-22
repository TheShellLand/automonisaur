import re


class Regex(object):

    def __init__(self):
        self.regex = None
        self.flags = None

    def re_email(self):
        self.regex = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
        return self

    def re_longitude_latitude(self):
        self.regex = r'([Long]{4}:[ ]?[0-9\.]*,[ ]?[Lat]{3}:[ ]?[0-9\.]*)'
        return self

    def config_ignorecase(self):
        self.flags = re.IGNORECASE
        return self

    def findall(self, search: str):
        return self._compile().findall(search)

    def fullmatch(self, search: str):
        return self._compile().fullmatch(search)

    def search(self, search: str):
        return self._compile().search(search)

    def _compile(self):
        if self.regex:
            return re.compile(self.regex, flags=self.flags)
        raise Exception(f'missing regex')


def geolocation(string):
    """Parse any kind of geolocation data"""

    # TODO: parse any geolocation info (long, lat)

    pattern = [
        r'([Long]{4}:[ ]?[0-9\.]*,[ ]?[Lat]{3}:[ ]?[0-9\.]*)'
    ]

    for p in pattern:
        c = re.compile(p)
        r = re.findall(c, string)

        if r:
            return r
