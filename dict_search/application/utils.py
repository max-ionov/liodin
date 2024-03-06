from typing import List

import yaml

from .datamodels import DictConfig


def load_dictionaries_config(config_path: str) -> List[DictConfig]:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return [DictConfig(**d) for d in config.get('dictionaries', [])]