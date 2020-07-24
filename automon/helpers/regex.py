import re

from automon.helpers import assertions
from automon.helpers.grok import GrokLegacy


def geolocation(string):
    """Parse any kind of geolocation data"""

    # TODO: parse any geolocation info (long, lat)

    pattern = [
        '([Long]{4}:[ ]?[0-9\.]*,[ ]?[Lat]{3}:[ ]?[0-9\.]*)'
    ]

    for p in pattern:
        c = re.compile(p)
        r = re.findall(c, string)

        if r:
            return r


class Magic:

    @staticmethod
    def magic_box(data: str) -> dict:
        """Do some grok magic on anything given and find everything"""

        all_matches = dict()
        grok = GrokLegacy.g

        for pattern in grok:

            try:
                compile_regex = re.compile(grok[pattern])  # compiled regex from g dict
                result = re.findall(compile_regex, data)  # regex search result

                if result:
                    list_results = []

                    if assertions.assert_list(result):
                        _list = result
                        for _item in _list:

                            if assertions.assert_tuple(_item):
                                _tuple = _item
                                for _item2 in _tuple:
                                    if len(_item2) > 0:
                                        list_results.append(_item2)

                            elif assertions.assert_string(_item):
                                if len(_item) > 0:
                                    list_results.append(_item)

                    if len(list_results) > 0:
                        all_matches[pattern] = list_results

            except Exception as err:
                # print('[!] Failed pattern: ' + grok_all_string[p] + ' => ' + str(err))
                pass

        return all_matches
