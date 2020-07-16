"""requires smidump"""

import os
import re
import yaml
import xmltodict
import subprocess

from automon.integrations.slack.slack_logger import SlackLogging
from automon.integrations.slack.slack_formatting import Chat
from automon.logger import Logging

log = Logging('snmp generator', level=Logging.INFO)
slacklog = SlackLogging(username='mibbot')


class SmidumpFormat:
    """smidump output formats"""

    def __init__(self):
        """
        Format types:
            cm            : reverse engineered conceptual model
            corba         : corba IDL interface and OID definitions (JIDM)
            identifiers   : list of all identifiers
            imports       : recursive list of all imports
            jax           : Java AgentX sub-agent classes in separate files
            metrics       : metrics characterizing MIB modules
            mosy          : intermediate format generated by the mosy compiler
            netsnmp       : ANSI C code for the NET-SNMP package
            perl          : Perl MIB dictionaries
            python        : Python MIB dictionaries
            sming         : SMIng
            smiv1         : SMIv1 (RFC 1155, RFC 1212, RFC 1215)
            smiv2         : SMIv2 (RFC 2578, RFC 2579, RFC 2580)
            sppi          : SPPI (RFC 3159)
            scli          : ANSI C manager stubs for the gsnmp package
            svg           : SVG diagram
            tree          : structure of the OID tree
            types         : recursive list of all derived types
            sizes         : RFC 3416 PDU sizes excluding message / transport headers
            xml           : intermediate SMI XML exchange format
            xsd           : XML schema definitions
            compliances   : compliances with all included objects / notifications
            yang          : YANG format
            boilerplate   : generate security considerations boilerplate text
        """
        self.cm = 'cm'
        self.corba = 'corba'
        self.identifiers = 'identifiers'
        self.imports = 'imports'
        self.jax = 'jax'
        self.metrics = 'metrics'
        self.mosy = 'mosy'
        self.netsnmp = 'netsnmp'
        self.perl = 'perl'
        self.python = 'py'
        self.sming = 'sming'
        self.smiv1 = 'smiv1'
        self.smiv2 = 'smiv2'
        self.sppi = 'sppi'
        self.scli = 'scli'
        self.svg = 'svg'
        self.tree = 'tree'
        self.sizes = 'sizes'
        self.xml = 'xml'
        self.xsd = 'xsd'
        self.compliances = 'compliances'
        self.yang = 'yang'
        self.boilerplate = 'boilerplate'

    def keys(self):
        return self.__dict__.keys()

    def get(self, key):
        return self.__dict__.get(key)

    def dict(self):
        return self.__dict__

    def get_type(self, value):
        for key in self.keys():
            if self.get(key) is value:
                return key

    def __str__(self):
        return f'{self.__dict__}'


class MibFile:
    def __init__(self, device: str, path: str):
        self.path = path
        self.device = device
        self.filename = os.path.split(path)[-1]

        if os.path.isfile(path):
            log.debug(f'found MIB {path}')
            # slacklog.debug(f'found MIB {mib.path}')
        else:
            msg = f'{MibFile} {path} not found'
            log.error(msg)
            slacklog.error(msg)
            raise

    def __str__(self):
        return self.path

    def read(self):
        return open(self.path).read()


class MibMap(MibFile):
    def __init__(self, MibFile: MibFile, stdout: bytes):
        self._MibFile = MibFile
        self._data = stdout
        self.device = self._MibFile.device
        self.path = self._MibFile.path
        self.filename = self._MibFile.filename
        self.len = len(self._data)
        self.oids = []

        try:
            self.xml = xmltodict.parse(self._data)
            self.smi = self.xml['smi']
        except:
            self.xml = None
            self.smi = None

    def update(self, oids: str):
        self.oids = oids

    def __str__(self):
        # return self.data.decode()
        if self.smi:
            return f'{self.smi}'
        else:
            return f'{self._data}'


class Oid(dict):
    def __init__(self, device: str, filename: str, oid_name: str, oid: str, description: str, unused: list):
        self.device = device
        self.module_name = self.device
        self.oid = oid
        self.oid_name = oid_name
        self.name = filename
        self.filename = self.name
        self.mib_file = self.name
        self.description = description
        self._unused = unused

    def __str__(self):
        return f'{self.device}, {self.filename}, {self.oid}, {self.description}'

    def __eq__(self, other):
        try:
            return (self.oid, self.description) == (other.oid, other.description)
        except AttributeError:
            return NotImplemented

    def __lt__(self, other):
        return self.oid < other.oid


class RequiredSmidump:
    def __init__(self):
        self.requires = 'smidump'

    def check(self) -> True or False:
        if os.system(f'which {self.requires}') == 0:
            log.debug(f'{self.requires} OK')
            # slacklog.debug(f'{self.requires} OK')
            return True
        else:
            msg = (
                f'missing {self.requires}, '
                f'please install {self.requires}, '
                f'`apt install smitools`')
            log.error(msg)
            slacklog.error(msg)
            return False


class PrometheusModule(dict):
    def __init__(self):
        self.template = {
            'modules': {}
        }
        self._modules = self.template.get('modules')

    def add_module(self, module_name: str,
                   version: int = 2,
                   retries: int = 3,
                   max_repetitions: int = 25,
                   timeout: str = '5s') -> dict:
        """Not all options are here"""
        template = {
            f'{module_name}': {
                'walk': [],
                'version': version,
                'retries': retries,
                'max_repetitions': max_repetitions,
                'timeout': timeout,
                'auth': {
                    'community': 'public'
                }
            }
        }
        self._modules.update(template)

    def _get_module(self, module_name: str) -> dict:
        if module_name not in self._modules.keys():
            self.add_module(module_name)
        return self._modules.get(module_name)

    def _get_walk(self, module_name: str) -> dict:
        return self._get_module(module_name)['walk']

    def _get_auth(self, module_name: str) -> dict:
        return self._get_module(module_name)['auth']

    def add_oid(self, oid: Oid, module_name: str = None, max_length: int = 40):
        module_name = module_name if module_name else oid.module_name

        template = f'{oid.oid_name}'.ljust(max_length + 3)

        walk = self._get_walk(module_name)
        walk.append(f'{template} # {oid.oid} {oid.description}')
        self.template = self._modules

    def add_auth(self, module_name: str = None,
                 community_string: str = 'public',
                 username: str = '', password: str = '',
                 security_level: str = 'noAuthNoPriv' or 'authNoPriv' or 'authPriv',
                 auth_protocol: str = 'MD5' or 'SHA',
                 priv_protocol: str = 'DES' or 'AES',
                 priv_password: str = '', context_name: str = '') -> dict:
        template = {
            'community': community_string,
            'username': username,
            'password': password,
            'security_level': security_level,
            'auth_protocol': auth_protocol,
            'priv_protocol': priv_protocol,
            'priv_password': priv_password,
            'context_name': context_name
        }
        module = self._get_auth(module_name)
        module.update(template)

    def __str__(self):
        return f'{self.template}'


class PrometheusGeneratorConfig(PrometheusModule):
    def __init__(self):
        self.template = PrometheusModule()
        self.config = self.template.template
        self.path = None
        self.filename = f'generator.yml'

    def _yaml_cleaner(self, yml: yaml.dump):
        yml = yml.replace("'", '')
        yml = yml.replace('"', '')

        return yml

    def _export_to_yaml(self):
        yml = yaml.dump(self.config, width=1200)
        yml = self._yaml_cleaner(yml)

        return yml

    def save_config(self, path: str = None):
        if path:
            output_file = os.path.join(path, self.filename)
        else:
            output_file = self.filename

        with open(output_file, 'w') as f:
            yml = self._export_to_yaml()
            f.write(yml)

        return yml

    def __str__(self):
        return self.template


class MIBS:
    def __init__(self, path: str, device: str = None):

        self.path = path

        # Check for smidump
        self._required = RequiredSmidump().check()

        if device:
            self.devices = [device]
        else:
            self.devices = os.listdir(self.path)

        self.mibs = []
        self.maps = []
        self.oids = []

        self._max_format = 0

        for device in self.devices:

            # self.device_path = os.path.join(MIBS_dir, device)
            path_to_device_folder = os.path.join(self.path, device)

            if os.path.isfile(path_to_device_folder):
                continue

            for mib_filename in os.listdir(path_to_device_folder):

                path_to_mib_file = os.path.join(path_to_device_folder, mib_filename)

                if os.path.isfile(path_to_mib_file):
                    if re.search('.mib$', mib_filename):
                        mib = MibFile(device, path_to_mib_file)
                        self.mibs.append(mib)
                else:
                    log.error(f'not found MIB {path_to_mib_file}')
                    slacklog.error(f'not found MIB {path_to_mib_file}')

    def _mib_generator(self) -> MibFile:
        for mib in self.mibs:
            yield mib

    def _map_generator(self) -> MibMap:
        for map in self.maps:
            yield map

    def _iod_generator(self) -> Oid:
        for iod in self.oids:
            yield iod

    def _create_oid_tuple(self, object: dict) -> tuple:

        if not isinstance(object, dict):
            return

        # [
        # 	('@name', 'l3EcmpGroupTableCurrentEntries'),
        # 	('@oid', '0.1.1.7'),
        # 	('@status', 'mandatory'),
        # 	('syntax', OrderedDict([('type', OrderedDict([
        # 			('@module', ''),
        # 			('@name', 'Integer32')
        # 		]))])),
        # 	('access', 'readonly'),
        # 	('description', 'Number of ECMP Group table entries currently in use.')
        # ];

        used_keys = ['@name', '@oid', 'description']

        if '@name' and '@oid' and 'description' in object.keys():

            oid_name = object.get('@name')
            oid = object.get('@oid')
            description = Chat.multi_to_single_line(object.get('description'))

            _unused_keys = [x for x in object.keys() if x is not used_keys]
            _unused = [(x, object.get(x)) for x in _unused_keys]

            if oid and description:
                if len(oid) > self._max_format:
                    self._max_format = len(oid)

                if len(oid_name) > self._max_format:
                    self._max_format = len(oid_name)

                return oid_name, oid, description, _unused

    def _list_walk(self, object: list) -> list:

        tuple_oids = []

        if not isinstance(object, list) or None:
            return tuple_oids

        for item in object:

            if isinstance(item, dict):
                tuple_oids.extend(self._dict_walk(item))
            else:
                log.critical(f'{self._list_walk} {NotImplemented}')

        return tuple_oids

    def _dict_walk(self, object: dict) -> list:

        tuple_oids = []

        if not isinstance(object, dict) or None:
            return []

        for key in object.keys():
            value = object.get(key)

            if isinstance(value, dict):
                tuple_oids.extend(self._dict_walk(value))
            elif isinstance(value, list):
                tuple_oids.extend(self._list_walk(value))
            elif not isinstance(value, str) and value is not None:
                log.critical(f'{self._dict_walk} {NotImplemented}')

            oid_and_description = self._create_oid_tuple(object)

            if oid_and_description and oid_and_description not in tuple_oids:
                tuple_oids.append(oid_and_description)

        return tuple_oids

    def _xml_walk(self, xml: dict) -> list:

        tuple_oids = []

        if isinstance(xml, dict):
            tuple_oids.extend(self._dict_walk(xml))
        elif isinstance(xml, list):
            tuple_oids.extend(self._list_walk(xml))
        else:
            log.critical(f'{self._xml_walk} {NotImplemented}')

        return tuple_oids

    def generate_prometheus_config(self) -> open:

        for mibmap in self._map_generator():

            filename = mibmap.filename
            xml = mibmap.smi
            device = mibmap.device

            list_of_oid_tuples = self._xml_walk(xml)
            # log.debug(list_of_oid_tuples)

            if not list_of_oid_tuples:
                continue

            oids = []

            for tuple_ in list_of_oid_tuples:
                oid_name, oid, description, _unused = tuple_

                oid = Oid(device=device, filename=filename, oid_name=oid_name, oid=oid, description=description,
                          unused=_unused)
                oids.append(oid)

                if oid not in self.oids:
                    self.oids.append(oid)

            mibmap.update(oids)

        # now create prometheus config
        prometheus_config = PrometheusGeneratorConfig()
        self.oids.sort()
        for _oid in self.oids:
            prometheus_config.template.add_oid(_oid, max_length=self._max_format)

        return prometheus_config.save_config(path=self.path)

    def generate_map(self, extension: SmidumpFormat = None) -> MibMap:

        def smidump_run(cmd: str, create_file: bool = False) -> None:

            if not self._required:
                return False

            run = subprocess.run(cmd.split(), capture_output=True)
            data = run.stdout
            data_out = data.decode()
            data_err = run.stderr.decode()

            if data_err:
                log.error(f'{data_err}')
                slacklog.error(f'```{data_err}```')

            map_ = MibMap(mib, data)
            self.maps.append(map_)

            if create_file:
                with open(map_.path, 'wb') as f:
                    f.write(map_._data)
                    log.debug(f'Wrote {map_.path} ({map_.len} B)')
                    slacklog.debug(f'Wrote {map_.path} ({map_.len} B)')

            return True

        for mib in self._mib_generator():

            path = mib.path
            device = mib.device

            if not re.search('.mib$', path):
                continue

            preload = ''
            for x in self.mibs:
                if x.device is device:
                    preload = preload + f' --preload={x.path}'

            if extension:
                smidump_format = SmidumpFormat().get_type(extension)
                map_file = f'{mib}_map.{extension}'
                opts = f'--level=6 -s -m -k -f {smidump_format}'

                cmd = f'smidump {opts} {preload} {mib}'

                log.debug(cmd)
                # slacklog.debug(cmd)
                smidump_run(cmd)

            elif extension is None:

                for smidump_format in SmidumpFormat().keys():
                    extension = getattr(SmidumpFormat(), smidump_format)
                    map_file = f'{mib}_map.{extension}'
                    opts = f'--level=6 -s -m -k -f {smidump_format}'

                    cmd = f'smidump {opts} {preload} {mib}'
                    # cmd = f'{self.smidump} {self.opts} {mib}'

                    log.debug(cmd)
                    # slacklog.debug(cmd)
                    smidump_run(cmd)

# m = MIBS(device='opengear', path='path/to/mibs')
# m.generate_map(SmidumpFormat().xml)
# yml = m.generate_prometheus_config()
#
# log.info('Done')
# slacklog.close()
