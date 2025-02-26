from urllib.parse import quote_plus

SELF = "'self'"


class BaseConfig(object):
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    DEPARTMENT_NAME = "The National Archives"
    DEPARTMENT_URL = "https://www.nationalarchives.gov.uk/"
    SERVICE_NAME = "AYR – Access Your Records"
    UNIVERSAL_VIEWER_SUPPORTED_IMAGE_TYPES = [
        "png",
        "jpg",
        "jpeg",
        "gif",
        "bmp",
        "ico",
        "tif",
        "tiff",
        "3fr",
        "arw",
        "cr2",
        "crw",
        "dcr",
        "dng",
        "erf",
        "k25",
        "kdc",
        "mef",
        "mos",
        "mrw",
        "nef",
        "orf",
        "pef",
        "ptx",
        "raf",
        "raw",
        "rw2",
        "sr2",
        "srf",
        "x3f",
        "heic",
        "heif",
        "jpe",
    ]
    UNIVERSAL_VIEWER_SUPPORTED_DOCUMENT_TYPES = [
        "pdf",
        "docx",
        "xlsx",
        "pptx",
        "odoc",
        "osheet",
        "oslides",
        "txt",
        "json",
        "md",
        "xml",
        "html",
        "htm",
    ]
    UNIVERSAL_VIEWER_SUPPORTED_OTHER_TYPES = [
        # text and Code Files
        "c",
        "cpp",
        "cs",
        "java",
        "py",
        "js",
        "jsx",
        "ts",
        "tsx",
        "php",
        "rb",
        "pl",
        "sql",
        "css",
        "scss",
        "less",
        "sh",
        "yaml",
        "yml",
        "xml",
        "xhtml",
        "plist",
        "properties",
        "bat",
        "cmd",
        "make",
        "groovy",
        "scala",
        "swift",
        "diff",
        "erl",
        "lst",
        "out",
        "patch",
        "sml",
        # archives and Compressed Files
        "zip",
        "rar",
        "7z",
        "gz",
        "bz2",
        "tar",
        "tgz",
        "tbz",
        "txz",
        # multimedia
        "mp3",
        "wav",
        "ogg",
        "mp4",
        "webm",
        # 3D
        "obj",
        "stl",
        "dae",
        "gltf",
        "glb",
        # other Formats
        "ps",
        "psd",
        "epub",
        "djvu",
        "csv",
    ]
    SUPPORTED_RENDER_EXTENSIONS = [
        *UNIVERSAL_VIEWER_SUPPORTED_DOCUMENT_TYPES,
        *UNIVERSAL_VIEWER_SUPPORTED_IMAGE_TYPES,
        *UNIVERSAL_VIEWER_SUPPORTED_OTHER_TYPES,
    ]

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
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}"
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
        return self._get_config_list(
            "CSP_DEFAULT_SRC", [SELF, self.FLASKS3_CDN_DOMAIN]
        )

    @property
    def CSP_CONNECT_SRC(self):
        return self._get_config_list(
            "CSP_CONNECT_SRC",
            [
                SELF,
                self.FLASKS3_CDN_DOMAIN,
                f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com",
            ],
        )

    @property
    def CSP_SCRIPT_SRC(self):
        return self._get_config_list(
            "CSP_SCRIPT_SRC",
            [
                SELF,
                self.FLASKS3_CDN_DOMAIN,
                f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com",
            ],
        )

    @property
    def CSP_SCRIPT_SRC_ELEM(self):
        return self._get_config_list(
            "CSP_SCRIPT_SRC_ELEM",
            [
                "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/",
                "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/",
            ],
        )

    @property
    def CSP_STYLE_SRC(self):
        return self._get_config_list("CSP_STYLE_SRC", [SELF])

    @property
    def CSP_STYLE_SRC_ELEM(self):
        return self._get_config_list(
            "CSP_STYLE_SRC_ELEM",
            [
                SELF,
                self.FLASKS3_CDN_DOMAIN,
                "https://cdn.jsdelivr.net/jsdelivr-header.css",
                "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/dist/uv.min.css",
            ],
        )

    @property
    def CSP_IMG_SRC(self):
        return self._get_config_list(
            "CSP_IMG_SRC", [SELF, self.FLASKS3_CDN_DOMAIN, "data:"]
        )

    @property
    def CSP_FRAME_SRC(self):
        return self._get_config_list(
            "CSP_FRAME_SRC",
            [SELF, f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com"],
        )

    @property
    def CSP_OBJECT_SRC(self):
        return self._get_config_list(
            "CSP_OBJECT_SRC",
            [SELF, f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com"],
        )

    @property
    def CSP_WORKER_SRC(self):
        return self._get_config_list(
            "CSP_WORKER_SRC", ["blob:", SELF, self.FLASKS3_CDN_DOMAIN]
        )

    def _get_config_value(self, variable_name):
        pass
