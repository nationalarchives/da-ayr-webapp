import os

from configs.base_config import BaseConfig


class EnvConfig(BaseConfig):

    def _get_config_value(self, variable_name):
        if os.getenv(variable_name) is not None:
            return os.getenv(variable_name)
        else:
            raise KeyError(f"{variable_name}")

    @property
    def S3_BUCKET_URL(self):
        aws_endpoint_url = os.getenv("AWS_ENDPOINT_URL")
        if aws_endpoint_url:
            return f"{aws_endpoint_url}/{self.RECORD_BUCKET_NAME}/"
        return super().S3_BUCKET_URL
