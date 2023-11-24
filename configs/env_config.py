import os

from configs.base_config import BaseConfig


class EnvConfig(BaseConfig):
    def _get_config_value(self, variable_name):
        return os.getenv(variable_name)
