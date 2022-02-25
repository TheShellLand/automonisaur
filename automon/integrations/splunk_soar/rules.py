import logging

from .phantom_unittest import import_playbook, container, results, artifact

timestamp = '%(asctime)s'
levelname = '%(levelname)s'
modname = '%(name)s'
message = '%(message)s'
log_format = f'{timestamp}\t{levelname}\t({modname})\t{message}'

logging.basicConfig(level=logging.DEBUG, format=log_format)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def playbook(playbook_to_import: str, container: dict = container(),
             name: str = '', callback: object = None):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{playbook.__name__}')

    # log.info(f'playbook_to_import: str, container: dict = {}, name: str, callback: object')

    log.debug(f'playbook_to_import: {playbook_to_import}')
    log.debug(f'container: {container}')
    log.debug(f'name: {name}')
    log.debug(f'callback: {callback}')

    return import_playbook(playbook_to_import)


def get_run_data(key: str, **kwargs):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{get_run_data.__name__}')

    # log.info(f'key: {key}')
    log.debug(f'key: {key}')

    return key


def condition(container: dict = container(), conditions: list = [], name: str = ''):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{condition.__name__}')

    log.debug(f'{help(condition)}')

    log.debug(f'container: {container}')
    log.debug(f'conditions: {conditions}')
    log.debug(f'name: {name}')

    return container, conditions, name


def format(container: dict = container(), template: str = '', parameters: list = [str],
           name: str = ''):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{format.__name__}')

    log.debug('container: dict = {}, template: str = '', parameters: list = [], name: str = ''')

    parameters_orig = parameters

    parameters = [
        [x.split(':')] for x in parameters
    ]

    log.debug(f'container: {container}')
    log.debug(f'template: {template}')
    log.debug(f'parameters: {parameters}')
    log.debug(f'name: {name}')

    return container, template, parameters, name


def get_format_data(name: str, **kwargs):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{get_format_data.__name__}')

    log.debug(f'name: {name}')

    return name


def collect2(container: dict = container(), datapath: list = [], action_results: object = None):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{collect2.__name__}')

    log.info('container: dict = {}, datapath: list = [], action_results: object = None')

    log.debug(f'container: {container}')
    log.debug(f'datapath: {datapath}')
    log.debug(f'action_results: {action_results}')

    return [[artifact(), artifact()]]


def act(action: str, parameters: str, assets: list, callback: object, name: str, parent_action: str = ''):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{act.__name__}')

    # log.info(f'action: str, parameters: str, assets: list, callback: object, name: str')

    log.debug(f'action: {action}')
    log.debug(f'parameters: {parameters}')
    log.debug(f'assets: {assets}')
    log.debug(f'callback: {callback}')
    log.debug(f'name: {name}')
    log.debug(f'parent_action: {parent_action}')

    return action, parameters, assets, callback, name, parent_action


def save_run_data(key: str, value: str, auto: bool):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{save_run_data.__name__}')

    log.debug(f'key: {key}')
    log.debug(f'value: {value}')
    log.debug(f'auto: {auto}')

    return key, value, auto


def debug(object: str):
    return log.debug(f'{object}')


def error(object: str):
    return log.error(f'{object}')
