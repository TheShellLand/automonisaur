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
