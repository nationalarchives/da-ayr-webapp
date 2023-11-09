import os

from configs.base_config import BaseConfig


class LocalConfig(BaseConfig):
    AWS_REGION = os.getenv("AWS_REGION", "")
    AWS_OPEN_SEARCH_INDEX = os.getenv("AWS_OPEN_SEARCH_INDEX", "")
    AWS_OPEN_SEARCH_HOST = os.getenv("AWS_OPEN_SEARCH_HOST", "")
    AWS_OPEN_SEARCH_USERNAME = os.getenv("AWS_OPEN_SEARCH_USERNAME", "")
    AWS_OPEN_SEARCH_PASSWORD = os.getenv("AWS_OPEN_SEARCH_PASSWORD", "")
    KEYCLOAK_BASE_URI = os.getenv("KEYCLOAK_BASE_URI", "")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "")
    KEYCLOAK_REALM_NAME = os.getenv("KEYCLOAK_REALM_NAME", "")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    KEYCLOAK_AYR_USER_GROUP = os.getenv("KEYCLOAK_AYR_USER_GROUP", "")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "")
