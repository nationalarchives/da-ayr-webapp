import os

import boto3

from app.main.aws.parameter import (
    get_aws_environment_prefix,
    get_parameter_store_key_value,
)
from configs.base_config import BaseConfig

# use only for local development
if os.environ.get("DEFAULT_AWS_PROFILE"):
    boto3.setup_default_session(
        profile_name=os.environ.get("DEFAULT_AWS_PROFILE")
    )


class AWSParameterStoreConfig(BaseConfig):
    @property
    def DB_PASSWORD(self):
        client = boto3.client("rds")
        token = client.generate_db_auth_token(
            DBHostname=self.DB_HOST,
            Port=self.DB_PORT,
            DBUsername=self.DB_USER,
            Region=self.AWS_REGION,
        )
        return token

    @property
    def _AWS_ENVIRONMENT_PREFIX(self):
        return get_aws_environment_prefix()

    def _get_config_value(self, variable_name):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + variable_name
        )
