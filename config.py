import os

from app.main.aws.parameter import (
    get_aws_environment_prefix,
    get_parameter_store_key_value,
)


class Config(object):
    APP_BASE_URL = os.environ.get("APP_BASE_URL", "")
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "")
    DEPARTMENT_URL = os.environ.get("DEPARTMENT_URL", "")
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "")
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "")
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "")
    SERVICE_URL = os.environ.get("SERVICE_URL", "")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True

    @property
    def AWS_ENVIRONMENT_PREFIX(self):
        return get_aws_environment_prefix() or os.getenv(
            "AWS_ENVIRONMENT_PREFIX"
        )

    @property
    def KEYCLOAK_BASE_URI(self):
        return get_parameter_store_key_value(
            self.AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_BASE_URI"
        ) or os.getenv("KEYCLOAK_BASE_URI")

    @property
    def KEYCLOAK_CLIENT_ID(self):
        return get_parameter_store_key_value(
            self.AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_CLIENT_ID"
        ) or os.getenv("KEYCLOAK_CLIENT_ID")

    @property
    def KEYCLOAK_REALM_NAME(self):
        return get_parameter_store_key_value(
            self.AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_REALM_NAME"
        ) or os.getenv("KEYCLOAK_REALM_NAME")

    @property
    def KEYCLOAK_CLIENT_SECRET(self):
        return get_parameter_store_key_value(
            self.AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_CLIENT_SECRET"
        ) or os.getenv("KEYCLOAK_CLIENT_SECRET")

    @property
    def KEYCLOAK_AYR_USER_GROUP(self):
        return get_parameter_store_key_value(
            get_aws_environment_prefix() + "KEYCLOAK_AYR_USER_GROUP"
        ) or os.getenv("KEYCLOAK_AYR_USER_GROUP")
