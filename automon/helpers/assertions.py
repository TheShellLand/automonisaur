import re
from ast import literal_eval

from automon.logger import Logging

log = Logging(__name__, Logging.DEBUG)


def make_tuple(obj):
    """Make a tuple from_this

    :param obj: string
    :return: tuple
    """
    return literal_eval(obj)


def assert_label(label):
    """Make sure neo4j label is formatted correctly
    """
    label = str(label)
    if label:
        if re.search('[:]', label):
            log.error(f"Invalid label '{label}': Remove the colon from the label")

        if not re.search('[a-zA-Z]', label[0]):  # First letter of a label must be a letter
            log.error(f"Invalid label '{label}': First character of Neo4j :LABEL must be a letter")
        else:
            return ':`' + label + '`'  # :`Label`
    else:
        return ''


def assert_tuple(obj):
    """Make sure it is a tuple
    """

    try:
        # isinstance(obj, tuple)
        if getattr(obj, '__getnewargs__') and not assert_string(obj) and not assert_list(obj):
            return True
    except:
        return False


def assert_dict(obj):
    """Make sure it is a dict
    """

    try:
        if getattr(obj, 'fromkeys') \
                and getattr(obj, 'popitem') \
                and getattr(obj, 'setdefault') \
                and getattr(obj, 'update') \
                and getattr(obj, 'values'):
            return True
    except:
        return False

    pass


def assert_list(obj):
    """Make sure it is a list

    :param obj: data
    :return: boolean
    """

    try:
        # isinstance(obj, list) and not isinstance(obj, str)
        if getattr(obj, 'append') and getattr(obj, 'sort') and getattr(obj, 'pop'):
            return True
    except:
        return False


def assert_string(obj):
    """Make sure it is a string

    :param obj: data
    :return: boolean
    """

    try:
        # isinstance(obj, str)
        if getattr(obj, 'strip') and getattr(obj, 'split') and getattr(obj, 'rstrip'):
            return True
    except:
        return False


def main():
    """Tests for dict, tuple, string, list

    :return: string
    """

    d = sorted(dir(dict(x=1)))
    t = sorted(dir(('a', 'b')))
    s = sorted(dir('1,'))
    l = sorted(dir([1]))

    dd = []
    tt = []
    ss = []
    ll = []

    for x in d:
        if x not in t and x not in s and x not in l:
            dd.append(x)

    for x in t:
        if x not in d and x not in l:
            tt.append(x)

    for x in s:
        if x not in d and x not in t and x not in l:
            ss.append(x)

    for x in l:
        if x not in d and x not in t and x not in s:
            ll.append(x)

    results = '''\
dict
{dict}

tuple
{tuple}

string
{string}

list
{list}'''.format(
        dict=dd,
        tuple=tt,
        string=ss,
        list=ll
    )

    print(results)


if __name__ == "__main__":
    main()
