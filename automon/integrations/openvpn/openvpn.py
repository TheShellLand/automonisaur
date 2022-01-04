import os
import io

from automon.integrations.minio import MinioClient, MinioConfig
from automon.log import Logging
from automon.helpers.sleeper import Sleeper

log = Logging(name='openvpn', level='info')


class ClientConfig:
    """ Create an OpenVPN client config
    """

    def __init__(self, name, hosts, options=None):
        """
        client
        dev tun
        remote example.com
        resolv-retry infinite
        nobind
        persist-key
        persist-tun
        ca [inline]
        cert [inline]
        key [inline]
        tls-auth [inline] 1
        verb 1
        keepalive 10 120
        port 1194
        proto udp
        cipher BF-CBC
        comp-lzo
        remote-cert-tls server

        <ca>
        </ca>

        <cert>
        </cert>

        <key>
        </key>

        <tls-auth>
        </tls-auth>
        """

        log.logging.debug('[ClientConfig] Creating new OpenVPN client config')

        self.name = name

        self.config = 'client\n'
        self.config += 'dev tun\n'

        for host in hosts:
            host, port, conn = host.split(':')
            self.config += f'remote {host} {port} {conn}\n'

        self.config += 'resolv-retry infinite\n'
        self.config += 'nobind\n'
        self.config += 'persist-key\n'
        self.config += 'persist-tun\n'
        self.config += 'ca [inline]\n'
        self.config += 'cert [inline]\n'
        self.config += 'key [inline]\n'
        self.config += 'tls-auth [inline] 1\n'
        self.config += 'verb 1\n'
        self.config += 'keepalive 10 120\n'
        self.config += 'cipher BF-CBC\n'
        self.config += 'comp-lzo\n'
        self.config += 'remote-cert-tls server\n'
        self.config += 'key-direction 1\n'

        if options:
            for option in options:
                self.config += option

        self.CONFIG = self.config.split('\n')

        self.ca = None
        self.cert = None
        self.key = None
        self.ta = None

    def add_ca(self, ca):
        self.ca = f'<ca>\n{ca.decode()}\n</ca>\n'

    def add_cert(self, cert):
        self.cert = f'<cert>\n{cert.decode()}\n</cert>\n'

    def add_key(self, key):
        self.key = f'<key>\n{key.decode()}\n</key>\n'

    def add_ta(self, ta):
        self.ta = f'<tls-auth>\n{ta.decode()}\n</tls-auth>\n'

    def build_config(self, prefix):

        config = self.config
        config += self.ca
        config += self.cert
        config += self.key
        config += self.ta

        if prefix:
            filename = prefix + '-' + self.name + '.ovpn'
        else:
            filename = self.name + '.ovpn'

        return filename, io.BytesIO(config.encode()), len(config)


def collector(minio_client, bucket, folder):
    """ Collect required files to build an OpenVPN client
    """
    log.logging.debug('[collector] Collecting all Minio bucket files')

    ca = None
    cert = []
    key = []
    ta = None

    for file in minio_client.list_objects(bucket, folder):

        file_path, file_name = os.path.split(file.object_name)
        folder = os.path.split(file_path)[-1]

        if file_name == 'ca.crt':
            download = minio_client.download_object(bucket, file)
            ca = download.data

        if file_name == 'ta.key':
            download = minio_client.download_object(bucket, file)
            ta = download.data

        if folder == 'issued':
            download = minio_client.download_object(bucket, file)
            data = download.data
            cert.append((file_name, data))

        if folder == 'private':
            download = minio_client.download_object(bucket, file)
            data = download.data
            key.append((file_name, data))

    return ca, cert, key, ta


def put_object(minio_client: MinioClient, bucket, client_configs, config_name, config_data, config_len):
    """ Minio object uploader
    """
    log.logging.debug(f'[put_object] Uploading: {config_name}')
    return minio_client.put_object(bucket, f'{client_configs}/{config_name}', config_data, config_len)


def create_configs(minio_client: MinioClient, bucket: str, client_configs: str,
                   ca: bytes, cert: list, key: list, ta: bytes, hosts: str, prefix, options=None):
    """ Create and upload OpenVPN Client config
    """
    for user, data in cert:
        name, _ = os.path.splitext(user)
        config = ClientConfig(name, hosts, options)
        config.add_ca(ca)
        config.add_ta(ta)
        config.add_cert(data)

        for k in key:
            k_name, k_data = k
            k_name, _ = os.path.splitext(k_name)

            if name == k_name:
                config.add_key(k_data)

        config_name, config_data, config_len = config.build_config(prefix)

        put_object(minio_client, bucket, client_configs, config_name, config_data, config_len)

        log.logging.debug(f'[create_configs] OpenVPN client config uploaded: {config_name}')


def run(minio_config: MinioConfig, openvpn_config):
    log.logging.info('Running...')

    while True:
        minio_config.secure = False
        minio_client = MinioClient(config=minio_config)

        minio_bucket = openvpn_config['bucket']
        openvpn_configs = openvpn_config['configs']

        for config in openvpn_configs:
            hosts = config['hosts']
            folder = os.path.relpath(config['folder'])
            keys = os.path.join(folder, 'pki')
            client_configs = os.path.join(folder, 'configs')
            try:
                prefix = config['prefix']
            except:
                prefix = None
            try:
                options = config['options']
            except:
                options = None

            ca, cert, key, ta = collector(minio_client, minio_bucket, keys)
            create_configs(minio_client, minio_bucket, client_configs, ca, cert, key, ta, hosts, prefix, options)

        log.logging.info('[build client configs] Finshed building all OpenVPN clients')
        log.logging.debug('[ClientConfig] sleeping')
        Sleeper.day('openvpn')


def test_run(minio_config: MinioConfig, openvpn_config):
    while True:
        minio_config.secure = False
        minio_client = MinioClient(minio_config)

        minio_bucket = openvpn_config['bucket']
        openvpn_configs = openvpn_config['configs']

        for config in openvpn_configs:
            hosts = config['hosts']
            folder = os.path.relpath(config['folder'])
            keys = os.path.join(folder, 'pki')
            client_configs = os.path.join(folder, 'configs')
            try:
                prefix = config['prefix']
            except:
                prefix = None
            try:
                options = config['options']
            except:
                options = None

            ca, cert, key, ta = collector(minio_client, minio_bucket, keys)
            create_configs(minio_client, minio_bucket, client_configs, ca, cert, key, ta, hosts, prefix, options)

            return True
