import logging

from automon.integrations.phantom.phantom_unittest import import_playbook

levelname = '%(levelname)s'
modname = '%(name)s'
message = '%(message)s'
log_format = f'{levelname}\t({modname})\t{message}'

logging.basicConfig(level=logging.DEBUG, format=log_format)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def playbook(playbook_to_import: str, container: str, name: str, callback: object):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{playbook.__name__}')

    log.info(f'playbook_to_import: str, container: str, name: str, callback: object')

    log.debug(playbook_to_import)
    log.debug(container)
    log.debug(name)
    log.debug(callback)

    return import_playbook(playbook_to_import)


def get_run_data(key: str, **kwargs):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{get_run_data.__name__}')

    log.info(f'key')

    log.debug(key)

    return key


def condition(container: str, conditions: list, name: str):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{condition.__name__}')

    log.debug(f'container: str, conditions: list, name: str')

    log.debug(container)
    log.debug(conditions)
    log.debug(name)

    return container, conditions, name


def format(container: object = None, template: str = None, parameters: list = None, name: str = None):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{format.__name__}')

    log.debug(f'container: object, template: str, parameters: list, name: str')

    log.debug(f'{container}')
    log.debug(f'{template}')
    log.debug(f'{parameters}')
    log.debug(f'{name}')

    return container, template, parameters, name


def get_format_data(name: str, **kwargs):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{get_format_data.__name__}')

    log.debug(f'name: {name}')

    return name


def act(action: str, parameters: str, assets: list, callback: object, name: str):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{act.__name__}')

    # log.info(f'action: str, parameters: str, assets: list, callback: object, name: str')

    log.debug(f'action: {action}')
    log.debug(f'parameters: {parameters}')
    log.debug(f'assets: {assets}')
    log.debug(f'callback: {callback}')
    log.debug(f'name: {name}')

    return action, parameters, assets, callback, name


def save_run_data(key: str, value: str, auto: bool):
    """Mock function"""
    log = logging.getLogger(f'{__name__}.{save_run_data.__name__}')

    log.debug(f'key: {key}')
    log.debug(f'value: {value}')
    log.debug(f'auto: {auto}')

    return key, value, auto


def debug(object: str):
    return log.info(f'{object}')


def error(object: str):
    return log.info(f'{object}')
