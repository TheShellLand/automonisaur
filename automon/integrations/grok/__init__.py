import os
import warnings
import pandas as pd

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.ERROR)


class Grok:
    def __init__(self):

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
        #             logger.info(f'skipping existing, {k}')

        df = pd.DataFrame(pd.concat(patterns))
        return df
