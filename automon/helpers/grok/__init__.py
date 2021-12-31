import os
import warnings
import pandas as pd

from automon.log import Logging


class Grok:
    def __init__(self):
        self._log = Logging(name=Grok.__name__, level=Logging.DEBUG)

        p = 'logstash-patterns-core/patterns'
        l = f'{os.path.join(os.path.split(os.path.realpath(__file__))[0])}'

        walk = os.walk(l)

        for folder, folders, files in walk:
            f_list = [os.path.join(folder, f) for f in files]

            if 'legacy' in folder:
                self.legacy_df = self.to_df(f_list)
                self.legacy = self.legacy_df.to_dict()[0]

            if 'ecs-v1' in folder:
                self.ecs_v1_df = self.to_df(f_list)
                self.ecs_v1 = self.ecs_v1_df.to_dict()[0]

        pass

    def to_df(self, files: list) -> pd.DataFrame:

        patterns = [self.to_pattern(f) for f in files]
        return self.expanded_dict(patterns)

    def to_pattern(self, file: str) -> pd.Series:
        filename = os.path.split(file)[-1]
        pattern = open(file, 'r').read()
        pattern = [x for x in pattern.splitlines() if '#' not in x if x]
        pattern = [x.split(' ') for x in pattern]
        pattern = {k[0]: ''.join(k[1:]) for k in pattern}

        return pd.Series(pattern).rename(filename)

    def expanded_dict(self, patterns: list) -> pd.DataFrame:

        # big_dict = {}
        # for d in patterns:
        #     for k, v in d.items():
        #         if k not in big_dict.keys():
        #             big_dict[k] = v
        #         else:
        #             self._log.info(f'skipping existing, {k}')

        df = pd.DataFrame(pd.concat(patterns))
        return df


class GrokLegacy:
    warnings.warn(f'GrokLegacy will be removed by v0.2.x', DeprecationWarning)
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
    g[
        'IPV6'] = '((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?'
    g[
        'IPV4'] = '(?<![0-9])(?:(?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5]))(?![0-9])'
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
    g['URI'] = g['URIPROTO'] + '://(?:' + g['USER'] + '(?::[^@]*)?@)?(?:' + g['URIHOST'] + ')?(?:' + g[
        'URIPATHPARAM'] + ')?'

    ##########################################
    # Months: January, Feb, 3, 03, 12, December
    ##########################################
    g[
        'MONTH'] = '\b(?:[Jj]an(?:uary|uar)?|[Ff]eb(?:ruary|ruar)?|[Mm](?:a|ä)?r(?:ch|z)?|[Aa]pr(?:il)?|[Mm]a(?:y|i)?|[Jj]un(?:e|i)?|[Jj]ul(?:y)?|[Aa]ug(?:ust)?|[Ss]ep(?:tember)?|[Oo](?:c|k)?t(?:ober)?|[Nn]ov(?:ember)?|[Dd]e(?:c|z)(?:ember)?)\b'
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
    g['TIMESTAMP_ISO8601'] = g['YEAR'] + '-' + g['MONTHNUM'] + '-' + g['MONTHDAY'] + '[T ]' + g['HOUR'] + ':?' + g[
        'MINUTE'] + '(?::?' + g['SECOND'] + ')?' + g['ISO8601_TIMEZONE'] + '?'
    g['DATE'] = g['DATE_US'] + '|' + g['DATE_EU']
    g['DATESTAMP'] = g['DATE'] + '[- ]' + g['TIME']
    g['TZ'] = '(?:[APMCE][SD]T|UTC)'
    g['DATESTAMP_RFC822'] = g['DAY'] + g['MONTH'] + g['MONTHDAY'] + g['YEAR'] + g['TIME'] + g['TZ']
    g['DATESTAMP_RFC2822'] = g['DAY'] + ', ' + g['MONTHDAY'] + ' ' + g['MONTH'] + ' ' + g['YEAR'] + ' ' + g[
        'TIME'] + ' ' + g['ISO8601_TIMEZONE']
    g['DATESTAMP_OTHER'] = g['DAY'] + ' ' + g['MONTH'] + ' ' + g['MONTHDAY'] + ' ' + g['TIME'] + ' ' + g['TZ'] + ' ' + \
                           g['YEAR']
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
    g[
        'LOGLEVEL'] = '([Aa]lert|ALERT|[Tt]race|TRACE|[Dd]ebug|DEBUG|[Nn]otice|NOTICE|[Ii]nfo|INFO|[Ww]arn?(?:ing)?|WARN?(?:ING)?|[Ee]rr?(?:or)?|ERR?(?:OR)?|[Cc]rit?(?:ical)?|CRIT?(?:ICAL)?|[Ff]atal|FATAL|[Ss]evere|SEVERE|EMERG(?:ENCY)?|[Ee]merg(?:ency)?)'

    def __init__(self):
        self._log = Logging(GrokLegacy.__name__, Logging.DEBUG)

        self.url = 'https://raw.githubusercontent.com/logstash-plugins/logstash-patterns-core/master/patterns/grok-patterns'
        # self.file = f'{os.path.split(os.path.realpath(__file__))[0]}/grok-patterns.txt'
        #
        # with open(self.file, 'r') as f:
        #     file = f.read()
        #
        #     parts = []
        #     section = []
        #
        #     for line in file.splitlines():
        #         if not line:
        #             continue
        #         if re.search('^#', line):
        #             parts.append(section)
        #             section = []
        #             section.append(line)
        #         else:
        #             section.append(line)
        #
        #         self._log.debug(line)

        # build dict from file

        # try url

        # compare file to url

        # if different, build dict from url
