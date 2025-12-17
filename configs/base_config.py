from .db_utils import build_database_url

SELF = "'self'"


UNIVERSAL_VIEWER_SUPPORTED_IMAGE_PUIDS = {
    "fmt/3": "gif",
    "fmt/4": "gif",
    "fmt/43": "jpg",
    "fmt/44": "jpg",
    "x-fmt/391": "jpg",
    "fmt/11": "png",
    "fmt/12": "png",
    "fmt/13": "png",
    "fmt/353": "tif",
    "fmt/567": "webp",
}

UNIVERSAL_VIEWER_SUPPORTED_APPLICATION_PUIDS = {
    "fmt/16": "pdf",
    "fmt/17": "pdf",
    "fmt/18": "pdf",
    "fmt/19": "pdf",
    "fmt/20": "pdf",
    "fmt/276": "pdf",
}

CONVERTIBLE_PUIDS = {
    "fmt/39": "doc",
    "fmt/40": "doc",
    "x-fmt/44": "doc",
    "x-fmt/45": "doc",
    "fmt/50": "rtf",
    "fmt/59": "xls",
    "fmt/61": "xls",
    "x-fmt/111": "txt",
    "x-fmt/116": "wk4",
    "fmt/126": "ppt",
    "fmt/214": "xlsx",
    "fmt/215": "pptx",
    "fmt/355": "rtf",
    "x-fmt/394": "wp",
    "fmt/412": "docx",
    "x-fmt/115": "wk3",
    "fmt/116": "bmp",
    "x-fmt/258": "vsd",
    "fmt/443": "vsd",
    "fmt/1510": "vsd",
    "x-fmt/255": "pub",
    "x-fmt/332": "fm3",
    "x-fmt/18": "csv",
}


class BaseConfig(object):
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    DEPARTMENT_NAME = "The National Archives"
    DEPARTMENT_URL = "https://www.nationalarchives.gov.uk/"
    SERVICE_NAME = "AYR – Access Your Records"
    UNIVERSAL_VIEWER_SUPPORTED_APPLICATION_PUIDS = (
        UNIVERSAL_VIEWER_SUPPORTED_APPLICATION_PUIDS
    )
    UNIVERSAL_VIEWER_SUPPORTED_IMAGE_PUIDS = (
        UNIVERSAL_VIEWER_SUPPORTED_IMAGE_PUIDS
    )
    SUPPORTED_RENDER_PUIDS = [
        *UNIVERSAL_VIEWER_SUPPORTED_APPLICATION_PUIDS,
        *UNIVERSAL_VIEWER_SUPPORTED_IMAGE_PUIDS,
    ]

    # Client-side cache durations (in seconds) for Universal Viewer assets
    UV_PAGE_IMAGE_CACHE_MAX_AGE = 300  # 5 minutes for full page images
    UV_THUMBNAIL_CACHE_MAX_AGE = 300  # 5 minutes for thumbnails
    UV_MANIFEST_CACHE_MAX_AGE = 300  # 5 minutes for IIIF manifests

    # Server-side cache durations (in seconds)
    PDF_S3_CACHE_TTL = 300  # 5 minutes for cached PDF bytes from S3

    @staticmethod
    def _parse_config_value(config_value):
        """Parses the configuration value into a list, applying necessary formatting."""
        if not config_value:
            return []
        return [
            (
                f"'{item.strip()}'"
                if item.strip().startswith("sha256")
                else item.strip()
            )
            for item in config_value.split(",")
        ]

    def _get_config_list(self, env_var, default_values):
        """Fetches and combines default values with additional values from configuration."""
        config_value = self._get_config_value(env_var)
        additional_values = self._parse_config_value(config_value)
        return default_values + additional_values

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
        try:
            ssl_mode = self._get_config_value("SQLALCHEMY_SSL_MODE")
        except KeyError:
            ssl_mode = "verify-full"
        return build_database_url(
            host=self.DB_HOST,
            port=self.DB_PORT,
            name=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            ssl_mode=ssl_mode,
            ssl_cert=self.DB_SSL_ROOT_CERTIFICATE,
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
    def ACCESS_COPY_BUCKET(self):
        return self._get_config_value("ACCESS_COPY_BUCKET")

    @property
    def S3_BUCKET_URL(self):
        return f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com"

    @property
    def ACCESS_COPY_BUCKET_URL(self):
        return f"https://{self.ACCESS_COPY_BUCKET}.s3.amazonaws.com"

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
    def OPEN_SEARCH_USE_SSL(self) -> bool:
        return self._get_config_value("OPEN_SEARCH_USE_SSL") == "true"

    @property
    def OPEN_SEARCH_VERIFY_CERTS(self) -> bool:
        return self._get_config_value("OPEN_SEARCH_VERIFY_CERTS") == "true"

    @property
    def PERF_TEST(self):
        return self._get_config_value("PERF_TEST") == "True"

    @property
    def CSP_DEFAULT_SRC(self):
        return [SELF, self.FLASKS3_CDN_DOMAIN]

    @property
    def CSP_CONNECT_SRC(self):
        return [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            self.S3_BUCKET_URL,
            self.ACCESS_COPY_BUCKET_URL,
        ]

    @property
    def CSP_SCRIPT_SRC(self):
        return [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            self.S3_BUCKET_URL,
            self.ACCESS_COPY_BUCKET_URL,
        ]

    @property
    def CSP_SCRIPT_SRC_ELEM(self):
        return [
            SELF,
            "https://cdn.jsdelivr.net/npm/universalviewer@4.2.0/",
        ]

    @property
    def CSP_STYLE_SRC(self):
        return [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
        ]

    @property
    def CSP_STYLE_SRC_ELEM(self):
        return [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            "https://cdn.jsdelivr.net/jsdelivr-header.css",
            "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='",  # pragma: allowlist secret
            "'sha256-7smvP9yjKljPbeD/NRIE3XgBZUTCaF936I8yK6wJUM4='",  # pragma: allowlist secret
            "'sha256-V4SarAiVbO77lJTzMaRut9Qr7Cx4R8jo8vH1dIFkVSc='",  # pragma: allowlist secret
            "https://cdn.jsdelivr.net/npm/universalviewer@4.2.0/dist/uv.min.css",
            "'sha256-5F6wlVbvqAuNSR7vsCpdIP/UhcVEa+hoNTMpejqmEkY='",  # pragma: allowlist secret
            # for pdfs
            "'sha256-d+KBcHLMVDIG87TjOCYsHdPCu+k2B7Tld0nSNiwUllY='",  # pragma: allowlist secret
        ]

    @property
    def CSP_IMG_SRC(self):
        return [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            self.S3_BUCKET_URL,
            self.ACCESS_COPY_BUCKET_URL,
            "data:",
        ]

    @property
    def CSP_FRAME_SRC(self):
        return [
            SELF,
            self.S3_BUCKET_URL,
            self.ACCESS_COPY_BUCKET_URL,
        ]

    @property
    def CSP_OBJECT_SRC(self):
        return [
            SELF,
            self.S3_BUCKET_URL,
            self.ACCESS_COPY_BUCKET_URL,
        ]

    @property
    def CSP_WORKER_SRC(self):
        return ["blob:", SELF, self.FLASKS3_CDN_DOMAIN]

    def _get_config_value(self, variable_name):
        pass
