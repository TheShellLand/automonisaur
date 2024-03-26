import re


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
