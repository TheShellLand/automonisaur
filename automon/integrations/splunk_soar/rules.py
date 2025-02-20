from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

from .phantom_unittest import import_playbook, container, results, artifact

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


def playbook(playbook_to_import: str, container: dict = container(),
             name: str = '', callback: object = None):
    """Mock function"""

    # logger.info(f'playbook_to_import: str, container: dict = {}, name: str, callback: object')

    logger.debug(f'playbook_to_import: {playbook_to_import}')
    logger.debug(f'container: {container}')
    logger.debug(f'name: {name}')
    logger.debug(f'callback: {callback}')

    return import_playbook(playbook_to_import)


def get_run_data(key: str, **kwargs):
    """Mock function"""

    # logger.info(f'key: {key}')
    logger.debug(f'key: {key}')

    return key


def condition(container: dict = container(), conditions: list = [], name: str = ''):
    """Mock function"""

    logger.debug(f'{help(condition)}')

    logger.debug(f'container: {container}')
    logger.debug(f'conditions: {conditions}')
    logger.debug(f'name: {name}')

    return container, conditions, name


def format(container: dict = container(), template: str = '', parameters: list = [str],
           name: str = ''):
    """Mock function"""

    logger.debug('container: dict = {}, template: str = '', parameters: list = [], name: str = ''')

    parameters_orig = parameters

    parameters = [
        [x.split(':')] for x in parameters
    ]

    logger.debug(f'container: {container}')
    logger.debug(f'template: {template}')
    logger.debug(f'parameters: {parameters}')
    logger.debug(f'name: {name}')

    return container, template, parameters, name


def get_format_data(name: str, **kwargs):
    """Mock function"""

    logger.debug(f'name: {name}')

    return name


def collect2(container: dict = container(), datapath: list = [], action_results: object = None):
    """Mock function"""

    logger.info('container: dict = {}, datapath: list = [], action_results: object = None')

    logger.debug(f'container: {container}')
    logger.debug(f'datapath: {datapath}')
    logger.debug(f'action_results: {action_results}')

    return [[artifact(), artifact()]]


def act(action: str, parameters: str, assets: list, callback: object, name: str, parent_action: str = ''):
    """Mock function"""

    # logger.info(f'action: str, parameters: str, assets: list, callback: object, name: str')

    logger.debug(f'action: {action}')
    logger.debug(f'parameters: {parameters}')
    logger.debug(f'assets: {assets}')
    logger.debug(f'callback: {callback}')
    logger.debug(f'name: {name}')
    logger.debug(f'parent_action: {parent_action}')

    return action, parameters, assets, callback, name, parent_action


def save_run_data(key: str, value: str, auto: bool):
    """Mock function"""

    logger.debug(f'key: {key}')
    logger.debug(f'value: {value}')
    logger.debug(f'auto: {auto}')

    return key, value, auto


def debug(object: str):
    return logger.debug(f'{object}')


def error(object: str):
    return logger.error(f'{object}')
