import os

from configs.base_config import BaseConfig


class EnvConfig(BaseConfig):

    def _get_config_value(self, variable_name):
        if os.getenv(variable_name) is not None:
            return os.getenv(variable_name)
        else:
            raise KeyError(f"{variable_name}")
