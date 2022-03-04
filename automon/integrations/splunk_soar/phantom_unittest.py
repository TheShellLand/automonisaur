import os
import importlib


class PhantomCompatableImporter:
    def __init__(self, file_name):
        self.use_case = file_name
        git_root = os.path.split(os.path.split(os.getcwd())[0])[0]
        import_file = os.path.join(git_root, self.use_case)

        temp = open(import_file, 'r').read().splitlines()
        self.compatible_import = ''.join(
            ['' if x == 'import phantom.rules as phantom' else f'{x}\n' for x in temp])

        # global spec
        # global helper
        spec = importlib.util.spec_from_loader('module', loader=None, origin=self.compatible_import)
        module = importlib.util.module_from_spec(spec)

        self.module = module

        exec(self.compatible_import, module.__dict__)


def import_playbook(playbook: str):
    playbook = playbook.strip()

    if 'master/' in playbook:
        playbook = playbook.replace('master/', '')
    return importlib.import_module(playbook)


def container():
    return {
        'id': 0
    }


def results():
    return [
        'cef_dictionary',
        'artifact_id'
    ]


def artifact(id_value: int = 0, source_data_identifier_value: str = '', results_item_1: list = results()):
    return {
            'container_id': id_value,
            'name': "User Validation",
            'contains': "{}",
            'source_data_identifier': source_data_identifier_value,
            'label': "enrich",
            'cef_value': "",
            'dedup_is_success': True,
            'run_automation': False,
            'cef_name': "",
            'cef_dictionary': results_item_1[0],
            # context (artifact id) is added to associate results with the artifact
            'context': {'artifact_id': results_item_1[1]},
        }