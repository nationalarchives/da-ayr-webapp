from urllib.parse import quote_plus

SELF = "'self'"


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
    SUPPORTED_RENDER_EXTENSIONS = ["pdf", "png", "jpg", "jpeg"]

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
    def DEFAULT_PAGE_SIZE(self) -> int:
        return int(self._get_config_value("DEFAULT_PAGE_SIZE"))

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

    @property
    def OPEN_SEARCH_HOST(self):
        return self._get_config_value("OPEN_SEARCH_HOST")

    @property
    def OPEN_SEARCH_HTTP_AUTH(self):
        return (
            self._get_config_value("OPEN_SEARCH_USERNAME"),
            self._get_config_value("OPEN_SEARCH_PASSWORD"),
        )

    @property
    def OPEN_SEARCH_CA_CERTS(self):
        return self._get_config_value("OPEN_SEARCH_CA_CERTS")

    @property
    def OPEN_SEARCH_TIMEOUT(self) -> int:
        return int(self._get_config_value("OPEN_SEARCH_TIMEOUT"))

    @property
    def PERF_TEST(self):
        return self._get_config_value("PERF_TEST") == "True"

    @property
    def CSP_DEFAULT_SRC(self):
        csp_default_src = self._get_config_value("CSP_DEFAULT_SRC")
        default_values = [SELF, self.FLASKS3_CDN_DOMAIN]
        if csp_default_src:
            additional_values = [
                item.strip() for item in csp_default_src.split(",")
            ]
            return default_values + additional_values
        return default_values

    @property
    def CSP_CONNECT_SRC(self):
        csp_connect_src = self._get_config_value("CSP_CONNECT_SRC")
        default_values = [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com",
        ]
        if csp_connect_src:
            additional_values = [
                item.strip() for item in csp_connect_src.split(",")
            ]
            return default_values + additional_values
        return default_values

    @property
    def CSP_SCRIPT_SRC(self):
        csp_script_src = self._get_config_value("CSP_SCRIPT_SRC")
        default_values = [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com",
        ]
        if csp_script_src:
            additional_values = [
                (
                    f"'{item.strip()}'"
                    if item.strip().startswith("sha256")
                    else item.strip()
                )
                for item in csp_script_src.split(",")
            ]
            return default_values + additional_values
        return default_values

    @property
    def CSP_SCRIPT_SRC_ELEM(self):
        csp_script_src_elem = self._get_config_value("CSP_SCRIPT_SRC_ELEM")
        default_values = [
            "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/",
            "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/",
        ]
        if csp_script_src_elem:
            additional_values = [
                (
                    f"'{item.strip()}'"
                    if item.strip().startswith("sha256")
                    else item.strip()
                )
                for item in csp_script_src_elem.split(",")
            ]
            return default_values + additional_values
        return default_values

    @property
    def CSP_STYLE_SRC(self):
        csp_style_src = self._get_config_value("CSP_STYLE_SRC")
        default_values = [
            SELF,
        ]
        if csp_style_src:
            additional_values = [
                (
                    f"'{item.strip()}'"
                    if item.strip().startswith("sha256")
                    else item.strip()
                )
                for item in csp_style_src.split(",")
            ]
            return default_values + additional_values
        return default_values

    @property
    def CSP_STYLE_SRC_ELEM(self):
        csp_style_src_elem = self._get_config_value("CSP_STYLE_SRC_ELEM")
        default_values = [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            "https://cdn.jsdelivr.net/jsdelivr-header.css",
            "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/dist/uv.min.css",
        ]
        if csp_style_src_elem:
            additional_values = [
                (
                    f"'{item.strip()}'"
                    if item.strip().startswith("sha256")
                    else item.strip()
                )
                for item in csp_style_src_elem.split(",")
            ]
            return default_values + additional_values
        return default_values

    @property
    def CSP_IMG_SRC(self):
        csp_img_src = self._get_config_value("CSP_IMG_SRC")
        default_values = [SELF, self.FLASKS3_CDN_DOMAIN, "data:"]
        if csp_img_src:
            additional_values = [
                (
                    f"'{item.strip()}'"
                    if item.strip().startswith("sha256")
                    else item.strip()
                )
                for item in csp_img_src.split(",")
            ]
            return default_values + additional_values
        return default_values

    @property
    def CSP_FRAME_SRC(self):
        csp_frame_src = self._get_config_value("CSP_FRAME_SRC")
        default_values = [
            SELF,
            f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com",
        ]
        if csp_frame_src:
            additional_values = [
                item.strip() for item in csp_frame_src.split(",")
            ]
            return default_values + additional_values
        return default_values

    @property
    def CSP_OBJECT_SRC(self):
        csp_object_src = self._get_config_value("CSP_OBJECT_SRC")
        default_values = [
            SELF,
            f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com",
        ]
        if csp_object_src:
            additional_values = [
                (
                    f"'{item.strip()}'"
                    if item.strip().startswith("sha256")
                    else item.strip()
                )
                for item in csp_object_src.split(",")
            ]
            return default_values + additional_values
        return default_values

    @property
    def CSP_WORKER_SRC(self):
        csp_worker_src = self._get_config_value("CSP_WORKER_SRC")
        default_values = [
            "blob:",
            SELF,
            self.FLASKS3_CDN_DOMAIN,
        ]
        if csp_worker_src:
            additional_values = [
                (
                    f"'{item.strip()}'"
                    if item.strip().startswith("sha256")
                    else item.strip()
                )
                for item in csp_worker_src.split(",")
            ]
            return default_values + additional_values
        return default_values

    def _get_config_value(self, variable_name):
        pass
