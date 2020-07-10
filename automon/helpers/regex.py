""" Grok brain; holds all the regular expression patterns of the world

Written         : Eric Jaw
Version         : 1.0
Created         : 2017-06-17

"""

import re
from automon.helpers import assertions


g = dict()
##########################################
# numbers, integer
##########################################
g['BASE10NUM'] = '(?<![0-9.+-])(?>[+-]?(?:(?:[0-9]+(?:\.[0-9]+)?)|(?:\.[0-9]+)))'
g['NUMBER'] = '(?:' + g['BASE10NUM'] + ')'
g['BASE16NUM'] = '(?<![0-9A-Fa-f])(?:[+-]?(?:0x)?(?:[0-9A-Fa-f]+))'
g['BASE16FLOAT'] = '\b(?<![0-9A-Fa-f.])(?:[+-]?(?:0x)?(?:(?:[0-9A-Fa-f]+(?:\.[0-9A-Fa-f]*)?)|(?:\.[0-9A-Fa-f]+)))\b'
g['POSINT'] = '\b(?:[1-9][0-9]*)\b'
g['NONNEGINT'] = '\b(?:[0-9]+)\b'

##########################################
# data
##########################################
g['WORD'] = '\b\w+\b'
g['NOTSPACE'] = '\S+'
g['SPACE'] = '\s*'
g['DATA'] = '.*?'
g['GREEDYDATA'] = '.*'
g['QUOTEDSTRING'] = '''(?>(?<!\\)(?>"(?>\\.|[^\\"]+)+"|""|(?>'(?>\\.|[^\\']+)+')|''|(?>`(?>\\.|[^\\`]+)+`)|``))'''
g['UUID'] = '[A-Fa-f0-9]{8}-(?:[A-Fa-f0-9]{4}-){3}[A-Fa-f0-9]{12}'
# URN, allowing use of RFC 2141 section 2.3 reserved characters'
g['URN'] = '''urn:[0-9A-Za-z][0-9A-Za-z-]{0,31}:(?:%[0-9a-fA-F]{2}|[0-9A-Za-z()+,.:=@;$_!*'/?#-])+'''

##########################################
# Networking
##########################################
g['CISCOMAC'] = '(?:(?:[A-Fa-f0-9]{4}\.){2}[A-Fa-f0-9]{4})'
g['WINDOWSMAC'] = '(?:(?:[A-Fa-f0-9]{2}-){5}[A-Fa-f0-9]{2})'
g['COMMONMAC'] = '(?:(?:[A-Fa-f0-9]{2}:){5}[A-Fa-f0-9]{2})'
g['MAC'] = '(?:' + g['CISCOMAC'] + '|' + g['WINDOWSMAC'] + '|' + g['COMMONMAC'] + '})'
g['IPV6'] = '((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?'
g['IPV4'] = '(?<![0-9])(?:(?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5]))(?![0-9])'
g['IP'] = '(?:' + g['IPV6'] + '|' + g['IPV4'] + ')'
g['HOSTNAME'] = '\b(?:[0-9A-Za-z][0-9A-Za-z-]{0,62})(?:\.(?:[0-9A-Za-z][0-9A-Za-z-]{0,62}))*(\.?|\b)'
g['IPORHOST'] = '(?:' + g['IP'] + ' |' + g['HOSTNAME'] + ')'
g['HOSTPORT'] = g['IPORHOST'] + ':' + g['POSINT']

##########################################
# user, email, account
##########################################
g['USERNAME'] = '[a-zA-Z0-9._-]+'
g['USER'] = g['USERNAME']
g['INT'] = '(?:[+-]?(?:[0-9]+))'
g['EMAILLOCALPART'] = '[a-zA-Z][a-zA-Z0-9_.+-=:]+'
g['EMAILADDRESS'] = g['EMAILLOCALPART'] + '@' + g['HOSTNAME']

##########################################
# paths
##########################################
g['UNIXPATH'] = '(/([\w_%!$@:.,+~-]+|\\.)*)+'
g['TTY'] = '(?:/dev/(pts|tty([pq])?)(\w+)?/?(?:[0-9]+))'
g['WINPATH'] = '(?>[A-Za-z]+:|\\)(?:\\[^\\?*]*)+'
g['URIPROTO'] = '[A-Za-z]+(\+[A-Za-z+]+)?'

# TODO: fix => :port
g['URIHOST'] = '' + g['IPORHOST'] + '(?::%{POSINT:port})?'
g['PATH'] = '(?:' + g['UNIXPATH'] + '|' + g['WINPATH'] + ')'
# uripath comes loosely from RFC1738, but mostly from what Firefox
# doesn't turn into %XX
g['URIPATH'] = '''(?:/[A-Za-z0-9$.+!*'(){},~:;=@#%&_\-]*)+'''
# g['URIPARAM'] = '\?(?:[A-Za-z0-9]+(?:=(?:[^&]*))?(?:&(?:[A-Za-z0-9]+(?:=(?:[^&]*))?)?)*)?'
g['URIPARAM'] = '''\?[A-Za-z0-9$.+!*'|(){},~@#%&/=:;_?\-\[\]<>]*'''
g['URIPATHPARAM'] = g['URIPATH'] + '(?:' + g['URIPARAM'] + ')?'
g['URI'] = g['URIPROTO'] + '://(?:' + g['USER'] + '(?::[^@]*)?@)?(?:' + g['URIHOST'] + ')?(?:' + g['URIPATHPARAM'] + ')?'

##########################################
# Months: January, Feb, 3, 03, 12, December
##########################################
g['MONTH'] = '\b(?:[Jj]an(?:uary|uar)?|[Ff]eb(?:ruary|ruar)?|[Mm](?:a|ä)?r(?:ch|z)?|[Aa]pr(?:il)?|[Mm]a(?:y|i)?|[Jj]un(?:e|i)?|[Jj]ul(?:y)?|[Aa]ug(?:ust)?|[Ss]ep(?:tember)?|[Oo](?:c|k)?t(?:ober)?|[Nn]ov(?:ember)?|[Dd]e(?:c|z)(?:ember)?)\b'
g['MONTHNUM'] = '(?:0?[1-9]|1[0-2])'
g['MONTHNUM2'] = '(?:0[1-9]|1[0-2])'
g['MONTHDAY'] = '(?:(?:0[1-9])|(?:[12][0-9])|(?:3[01])|[1-9])'

##########################################
# Days: Monday, Tue, Thu, etc...
##########################################
g['DAY'] = '(?:Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)'

##########################################
# Years?
##########################################
g['YEAR'] = '(?>\d\d){1,2}'
g['HOUR'] = '(?:2[0123]|[01]?[0-9])'
g['MINUTE'] = '(?:[0-5][0-9])'
# '60' is a leap second in most time standards and thus is valid.
g['SECOND'] = '(?:(?:[0-5]?[0-9]|60)(?:[:.,][0-9]+)?)'
g['TIME'] = '(?!<[0-9])' + g['HOUR'] + ':' + g['MINUTE'] + '(?::' + g['SECOND'] + ')(?![0-9])'
# datestamp is YYYY/MM/DD-HH:MM:SS.UUUU (or something like it)
g['DATE_US'] = g['MONTHNUM'] + '[/-]' + g['MONTHDAY'] + '[/-]' + g['YEAR']
g['DATE_EU'] = g['MONTHDAY'] + '[./-]' + g['MONTHNUM'] + './-]' + g['YEAR']
g['ISO8601_TIMEZONE'] = '(?:Z|[+-]' + g['HOUR'] + '(?::?' + g['MINUTE'] + '))'
g['ISO8601_SECOND'] = '(?:' + g['SECOND'] + '|60)'
g['TIMESTAMP_ISO8601'] = g['YEAR'] + '-' + g['MONTHNUM'] + '-' + g['MONTHDAY'] + '[T ]' + g['HOUR'] + ':?' + g['MINUTE'] + '(?::?' + g['SECOND'] + ')?' + g['ISO8601_TIMEZONE'] + '?'
g['DATE'] = g['DATE_US'] + '|' + g['DATE_EU']
g['DATESTAMP'] = g['DATE'] + '[- ]' + g['TIME']
g['TZ'] = '(?:[APMCE][SD]T|UTC)'
g['DATESTAMP_RFC822'] = g['DAY'] + g['MONTH'] + g['MONTHDAY'] + g['YEAR'] + g['TIME'] + g['TZ']
g['DATESTAMP_RFC2822'] = g['DAY'] + ', ' + g['MONTHDAY'] + ' ' + g['MONTH'] + ' ' + g['YEAR'] + ' ' + g['TIME'] + ' ' + g['ISO8601_TIMEZONE']
g['DATESTAMP_OTHER'] = g['DAY'] + ' ' + g['MONTH'] + ' ' + g['MONTHDAY'] + ' ' + g['TIME'] + ' ' + g['TZ'] + ' ' + g['YEAR']
g['DATESTAMP_EVENTLOG'] = g['YEAR'] + g['MONTHNUM2'] + g['MONTHDAY'] + g['HOUR'] + g['MINUTE'] + g['SECOND']

##########################################
# Syslog Dates: Month Day HH:MM:SS
##########################################
g['SYSLOGTIMESTAMP'] = g['MONTH'] + ' +' + g['MONTHDAY'] + ' ' + g['TIME']
g['PROG'] = '[\x21-\x5a\x5c\x5e-\x7e]+'
# TODO: fix => :program :pid
g['SYSLOGPROG'] = '%{PROG:program}(?:\[%{POSINT:pid}\])?'
g['SYSLOGHOST'] = g['IPORHOST']
# TODO: fix => :facility :priority
g['SYSLOGFACILITY'] = '<%{NONNEGINT:facility}.%{NONNEGINT:priority}>'
g['HTTPDATE'] = g['MONTHDAY'] + '/' + g['MONTH'] + '/' + g['YEAR'] + ':' + g['TIME'] + ' ' + g['INT']

##########################################
# Shortcuts
##########################################
g['QS'] = g['QUOTEDSTRING']

##########################################
# Log formats
##########################################
# TODO: fix => these :timestamp :logsource
g['SYSLOGBASE'] = '%{SYSLOGTIMESTAMP:timestamp} (?:%{SYSLOGFACILITY} )?%{SYSLOGHOST:logsource} %{SYSLOGPROG}:'

##########################################
# Geolocation
##########################################
# TODO: add geolocation regex
# g['GEO'] = ''

##########################################
# Log Levels
##########################################
g['LOGLEVEL'] = '([Aa]lert|ALERT|[Tt]race|TRACE|[Dd]ebug|DEBUG|[Nn]otice|NOTICE|[Ii]nfo|INFO|[Ww]arn?(?:ing)?|WARN?(?:ING)?|[Ee]rr?(?:or)?|ERR?(?:OR)?|[Cc]rit?(?:ical)?|CRIT?(?:ICAL)?|[Ff]atal|FATAL|[Ss]evere|SEVERE|EMERG(?:ENCY)?|[Ee]merg(?:ency)?)'


def geolocation(string):
    """Parse any kind of geolocation data

    :param string:
    :return:
    """

    # TODO: parse any geolocation info (long, lat)

    pattern = [
        '([Long]{4}:[ ]?[0-9\.]*,[ ]?[Lat]{3}:[ ]?[0-9\.]*)'
    ]

    for p in pattern:
        c = re.compile(p)
        r = re.findall(c, string)

        if r:
            return r


def magic(data):
    """Do some grok magic on anything given and find everything

    :param data:
    :return:
    """

    magic_box = dict()

    for p in g:

        try:
            c = re.compile(g[p])  # compiled regex from g dict
            r = re.findall(c, data)  # regex search result

            if r:
                l = []

                if assertions.assert_list(r):
                    _list = r
                    for _item in _list:

                        if assertions.assert_tuple(_item):
                            _tuple = _item
                            for _item2 in _tuple:
                                if len(_item2) > 0:
                                    l.append(_item2)

                        elif assertions.assert_string(_item):
                            if len(_item) > 0:
                                l.append(_item)

                if len(l) > 0:
                    magic_box[p] = l

        except Exception as err:
            # print('[!] Failed pattern: ' + grok_all_string[p] + ' => ' + str(err))
            pass

    return magic_box


def main():
    test = '100.15.96.234 helehleeajd'
    print('[*] Found: ' + str(magic(test)))


if __name__ == "__main__":
    main()
