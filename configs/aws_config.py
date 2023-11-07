import os

import boto3

from app.main.aws.parameter import (
    get_aws_environment_prefix,
    get_parameter_store_key_value,
)
from configs.base_config import Config

# use only for local development
if os.environ.get("DEFAULT_AWS_PROFILE"):
    boto3.setup_default_session(
        profile_name=os.environ.get("DEFAULT_AWS_PROFILE")
    )


class AWSConfig(Config):
    @property
    def _AWS_ENVIRONMENT_PREFIX(self):
        return get_aws_environment_prefix()

    @property
    def AWS_REGION(self):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + "AWS_REGION"
        )

    @property
    def AWS_OPEN_SEARCH_INDEX(self):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + "AWS_OPEN_SEARCH_INDEX"
        )

    @property
    def AWS_OPEN_SEARCH_HOST(self):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + "AWS_OPEN_SEARCH_HOST"
        )

    @property
    def AWS_OPEN_SEARCH_USERNAME(self):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + "AWS_OPEN_SEARCH_USERNAME"
        )

    @property
    def AWS_OPEN_SEARCH_PASSWORD(self):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + "AWS_OPEN_SEARCH_PASSWORD"
        )

    @property
    def KEYCLOAK_BASE_URI(self):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_BASE_URI"
        )

    @property
    def KEYCLOAK_CLIENT_ID(self):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_CLIENT_ID"
        )

    @property
    def KEYCLOAK_REALM_NAME(self):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_REALM_NAME"
        )

    @property
    def KEYCLOAK_CLIENT_SECRET(self):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_CLIENT_SECRET"
        )

    @property
    def KEYCLOAK_AYR_USER_GROUP(self):
        return get_parameter_store_key_value(
            self._AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_AYR_USER_GROUP"
        )
