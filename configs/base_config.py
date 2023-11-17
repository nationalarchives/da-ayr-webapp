class BaseConfig(object):
    RATELIMIT_HEADERS_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    CONTACT_EMAIL = "contact email"
    CONTACT_PHONE = "contact phone"
    DEPARTMENT_NAME = "The National Archives"
    DEPARTMENT_URL = "https://www.nationalarchives.gov.uk/"
    SERVICE_NAME = "AYR - Access Your Records"
    SERVICE_PHASE = "BETA"
    SERVICE_URL = "https://ayr.nationalarchives.gov.uk/"

    @property
    def AWS_REGION(self):
        return self._get_config_value("AWS_REGION")

    @property
    def AWS_OPEN_SEARCH_INDEX(self):
        return self._get_config_value("AWS_OPEN_SEARCH_INDEX")

    @property
    def AWS_OPEN_SEARCH_HOST(self):
        return self._get_config_value("AWS_OPEN_SEARCH_HOST")

    @property
    def AWS_OPEN_SEARCH_USERNAME(self):
        return self._get_config_value("AWS_OPEN_SEARCH_USERNAME")

    @property
    def AWS_OPEN_SEARCH_PASSWORD(self):
        return self._get_config_value("AWS_OPEN_SEARCH_PASSWORD")

    @property
    def KEYCLOAK_BASE_URI(self):
        return self._get_config_value("KEYCLOAK_BASE_URI")

    @property
    def KEYCLOAK_CLIENT_ID(self):
        return self._get_config_value("KEYCLOAK_CLIENT_ID")

    @property
    def KEYCLOAK_REALM_NAME(self):
        return self._get_config_value("KEYCLOAK_REALM_NAME")

    @property
    def KEYCLOAK_CLIENT_SECRET(self):
        return self._get_config_value("KEYCLOAK_CLIENT_SECRET")

    @property
    def KEYCLOAK_AYR_USER_GROUP(self):
        return self._get_config_value("KEYCLOAK_AYR_USER_GROUP")

    @property
    def RATELIMIT_STORAGE_URI(self):
        return self._get_config_value("RATELIMIT_STORAGE_URI")

    @property
    def SECRET_KEY(self):
        return self._get_config_value("SECRET_KEY")

    def _get_config_value(self, variable_name):
        pass
