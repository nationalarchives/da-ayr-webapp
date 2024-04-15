import os

from configs.base_config import BaseConfig


class EnvConfig(BaseConfig):
    def _get_config_value(self, variable_name):
        if variable_name in (
            "AWS_REGION",
            "FLASKS3_ACTIVE",
            "FLASKS3_CDN_DOMAIN",
            "FLASKS3_BUCKET_NAME",
        ):
            return os.getenv(variable_name)

        if os.getenv(variable_name) is not None:
            return os.getenv(variable_name)
        else:
            raise Exception(
                f"variable name : '{variable_name}' has not been set in .env file"
            )
