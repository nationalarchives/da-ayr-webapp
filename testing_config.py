import os

from config import Config


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "TEST_SECRET_KEY"  # pragma: allowlist secret
    WTF_CSRF_ENABLED = False

    @property
    def AWS_ENVIRONMENT_PREFIX(self):
        return os.getenv("AWS_ENVIRONMENT_PREFIX")

    @property
    def AWS_REGION(self):
        return os.getenv("AWS_REGION")

    @property
    def AWS_OPEN_SEARCH_INDEX(self):
        return os.getenv("AWS_OPEN_SEARCH_INDEX")

    @property
    def AWS_OPEN_SEARCH_HOST(self):
        return os.getenv("AWS_OPEN_SEARCH_HOST")

    @property
    def AWS_OPEN_SEARCH_USERNAME(self):
        return os.getenv("AWS_OPEN_SEARCH_USERNAME")

    @property
    def AWS_OPEN_SEARCH_PASSWORD(self):
        return os.getenv("AWS_OPEN_SEARCH_PASSWORD")

    @property
    def KEYCLOAK_BASE_URI(self):
        return os.getenv("KEYCLOAK_BASE_URI")

    @property
    def KEYCLOAK_CLIENT_ID(self):
        return os.getenv("KEYCLOAK_CLIENT_ID")

    @property
    def KEYCLOAK_REALM_NAME(self):
        return os.getenv("KEYCLOAK_REALM_NAME")

    @property
    def KEYCLOAK_CLIENT_SECRET(self):
        return os.getenv("KEYCLOAK_CLIENT_SECRET")

    @property
    def KEYCLOAK_AYR_USER_GROUP(self):
        return os.getenv("KEYCLOAK_AYR_USER_GROUP")
