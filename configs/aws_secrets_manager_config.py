import json
import os

import boto3

from configs.base_config import BaseConfig

# use only for local development
if os.environ.get("DEFAULT_AWS_PROFILE"):
    boto3.setup_default_session(
        profile_name=os.environ.get("DEFAULT_AWS_PROFILE")
    )


class AWSSecretsManagerConfig(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        self.secrets_dict = self._get_secrets_manager_config_dict(
            os.getenv("AWS_SM_CONFIG_SECRET_ID")
        )

    def _get_secrets_manager_config_dict(self, secret_id):
        """
        Get dict of secret values using `secret_id` in Secrets Manager.
        :param secret_id: The ID of the Secrets Manager store to retrieve data from.
        :return: Dict representing the values inside the store
        """
        client = boto3.client(
            service_name="secretsmanager",
        )

        secret_value_json_string = client.get_secret_value(SecretId=secret_id)[
            "SecretString"
        ]
        secrets_dict = json.loads(secret_value_json_string)

        return secrets_dict

    def _get_config_value(self, variable_name):
        """
        Get a specific value from inside the Secrets Manager dict using `variable_name`.
        :param variable_name: Key of the value that should be retrieved.
        :return: Value of the retrieved secret
        """
        return self.secrets_dict[variable_name]

    @property
    def KEYCLOAK_CLIENT_SECRET(self):
        return self._get_secrets_manager_config_dict(
            os.getenv("AWS_SM_KEYCLOAK_CLIENT_SECRET_ID")
        )["SECRET"]
