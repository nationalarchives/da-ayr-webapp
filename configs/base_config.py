from urllib.parse import quote_plus


class BaseConfig(object):
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    CONTACT_EMAIL = "contact email"
    CONTACT_PHONE = "contact phone"
    DEPARTMENT_NAME = "The National Archives"
    DEPARTMENT_URL = "https://www.nationalarchives.gov.uk/"
    SERVICE_NAME = "AYR – Access Your Records"
    SERVICE_PHASE = "BETA"
    SERVICE_URL = "https://ayr.nationalarchives.gov.uk/"

    @property
    def AWS_REGION(self):
        return self._get_config_value("AWS_REGION")

    @property
    def DB_HOST(self):
        return self._get_config_value("DB_HOST")

    @property
    def DB_PORT(self):
        return self._get_config_value("DB_PORT")

    @property
    def DB_USER(self):
        return self._get_config_value("DB_USER")

    @property
    def DB_PASSWORD(self):
        return self._get_config_value("DB_PASSWORD")

    @property
    def DB_NAME(self):
        return self._get_config_value("DB_NAME")

    @property
    def DB_SSL_ROOT_CERTIFICATE(self):
        return self._get_config_value("DB_SSL_ROOT_CERTIFICATE")

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return (
            "postgresql+psycopg2://"
            f"{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?sslmode=verify-full&sslrootcert={self.DB_SSL_ROOT_CERTIFICATE}"
        )

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
    def SECRET_KEY(self):
        return self._get_config_value("SECRET_KEY")

    @property
    def DEFAULT_PAGE_SIZE(self):
        return self._get_config_value("DEFAULT_PAGE_SIZE")

    @property
    def DEFAULT_DATE_FORMAT(self):
        return self._get_config_value("DEFAULT_DATE_FORMAT")

    @property
    def RECORD_BUCKET_NAME(self):
        return self._get_config_value("RECORD_BUCKET_NAME")

    @property
    def FLASKS3_ACTIVE(self):
        return self._get_config_value("FLASKS3_ACTIVE") == "True"

    @property
    def FLASKS3_CDN_DOMAIN(self):
        return self._get_config_value("FLASKS3_CDN_DOMAIN")

    @property
    def FLASKS3_BUCKET_NAME(self):
        return self._get_config_value("FLASKS3_BUCKET_NAME")

    def _get_config_value(self, variable_name):
        pass
