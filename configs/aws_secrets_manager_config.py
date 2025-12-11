import json
import os

import boto3
from requests_aws4auth import AWS4Auth

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
        self._db_config = None

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

    def refresh_db_secret(self):
        """
        Force refresh DB credentials from Secrets Manager.
        Called when SQL fails with authentication error.
        """
        print("Refreshing Password db_secret")
        self._db_config = self._get_secrets_manager_config_dict(
            os.getenv("AWS_SM_DB_CONFIG_SECRET_ID")
        )

    @property
    def KEYCLOAK_CLIENT_SECRET(self):
        return self._get_secrets_manager_config_dict(
            os.getenv("AWS_SM_KEYCLOAK_CLIENT_SECRET_ID")
        )["SECRET"]

    @property
    def _DB_CONFIG(self):
        """
        Lazy-load the DB secret only once.
        Rotated secrets are picked up via refresh_db_secret().
        """
        if self._db_config is None:
            self.refresh_db_secret()
        return self._db_config

    @property
    def DB_HOST(self):
        return self._DB_CONFIG["proxy"]

    @property
    def DB_PORT(self):
        return self._DB_CONFIG["port"]

    @property
    def DB_USER(self):
        return self._DB_CONFIG["username"]

    @property
    def DB_PASSWORD(self):
        return self._DB_CONFIG["password"]

    @property
    def DB_NAME(self):
        return self._DB_CONFIG["dbname"]

    def build_sqlalchemy_uri(self):
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def OPEN_SEARCH_HTTP_AUTH(self):
        session = boto3.Session()
        credentials = session.get_credentials()
        auth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            self.AWS_REGION,
            "es",
            session_token=credentials.token,
        )
        return auth
