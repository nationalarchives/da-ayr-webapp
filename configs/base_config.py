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
        return [SELF, self.FLASKS3_CDN_DOMAIN]

    @property
    def CSP_CONNECT_SRC(self):
        return [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com",
        ]

    @property
    def CSP_SCRIPT_SRC(self):
        return [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com",
            "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/",
            "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/",
            "'sha256-GUQ5ad8JK5KmEWmROf3LZd9ge94daqNvd8xy9YS1iDw='",  # pragma: allowlist secret
            "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",  # pragma: allowlist secret
            "'sha256-JTVvglOxxHXAPZcB40r0wZGNZuFHt0cm0bQVn8LK5GQ='",  # pragma: allowlist secret
            "'sha256-LnUrbI34R6DmHbJR754/DQ0b/JKCTdo/+BKs5oLAyNY='",  # pragma: allowlist secret
            "'sha256-74nJjfZHR0MDaNHtes/sgN253tXMCsa4SeniH8bU3x8='",  # pragma: allowlist secret
            "'sha256-NDFO9Q6S8WUwG5n8w7gRLvvPrhqj72CJNXzZVcbOwG8='",  # pragma: allowlist secret
            "'sha256-bxI3qvjziRybgoaeQYcUjRHcCTdbUu/A9xFMlfNGZAQ='",  # pragma: allowlist secret
        ]

    @property
    def CSP_SCRIPT_SRC_ELEM(self):
        return [
            # -- stg --
            "https://d1598aa5u2vnrm.cloudfront.net/assets/govuk-frontend.min.js",
            "https://d1598aa5u2vnrm.cloudfront.net/assets/init.uv.js",
            # -- np --
            "https://dfnwzvjz3kfu4.cloudfront.net/assets/govuk-frontend.min.js",
            "https://dfnwzvjz3kfu4.cloudfront.net/assets/init.uv.js",
            "https://d2tm6k52k7dws9.cloudfront.net/assets/govuk-frontend.min.js",
            "https://d2tm6k52k7dws9.cloudfront.net/assets/init.uv.js",
            # -- p --
            "https://d26l7zu9rvd0xp.cloudfront.net/assets/govuk-frontend.min.js",
            "https://d26l7zu9rvd0xp.cloudfront.net/assets/init.uv.js",
            "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/",
            "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/",
            "'sha256-GUQ5ad8JK5KmEWmROf3LZd9ge94daqNvd8xy9YS1iDw='",  # pragma: allowlist secret
            "'sha256-bxI3qvjziRybgoaeQYcUjRHcCTdbUu/A9xFMlfNGZAQ='",  # pragma: allowlist secret
            "'sha256-JTVvglOxxHXAPZcB40r0wZGNZuFHt0cm0bQVn8LK5GQ='",  # pragma: allowlist secret
        ]

    @property
    def CSP_STYLE_SRC(self):
        return [
            SELF,
            "'sha256-aqNNdDLnnrDOnTNdkJpYlAxKVJtLt9CtFLklmInuUAE='",  # pragma: allowlist secret
            "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='",  # pragma: allowlist secret
            "'sha256-s6M/FyyCCegtJyBnH26lkxb67XZxuZKosiCQWD+VaSo='",  # pragma: allowlist secret
            "'sha256-gNGYzcxL9BKlQFzUxh3BgvhKn2szEIFgg65uQvfaxiI='",  # pragma: allowlist secret
            "'sha256-jcxDeNpsDPUI+dIIqUyA3VBoLgf3Mi2LkRWL/H61who='",  # pragma: allowlist secret
            "'sha256-crS7z4MA9wqqtYsAtmJ6LiW05hz4QJTaokDTQAzc+Hs='",  # pragma: allowlist secret
            "'sha256-8Vn73Z5msbLVngI0nj0OnoRknDpixmr5Qqxqq1oVeyw='",  # pragma: allowlist secret
            "'sha256-1u1O/sNzLBXqLGKzuRbVTI5abqBQBfKsNv3bH5iXOkg='",  # pragma: allowlist secret
            "'sha256-xDT4BUH+7vjNzOH1DSYRS8mdxJbvLVPYsb8hjk4Yccg='",  # pragma: allowlist secret
            "'sha256-ylK9YBCBEaApMPzc82Ol5H/Hd5kmcv3wQlT3Y5m7Kn4='",  # pragma: allowlist secret
            "'sha256-0EZqoz+oBhx7gF4nvY2bSqoGyy4zLjNF+SDQXGp/ZrY='",  # pragma: allowlist secret
        ]

    @property
    def CSP_STYLE_SRC_ELEM(self):
        return [
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            # -- stg --
            "https://d1598aa5u2vnrm.cloudfront.net/assets/govuk-frontend-4.7.0.min.css",
            "https://d1598aa5u2vnrm.cloudfront.net/assets/src/css/main.css",
            # -- np --
            "https://dfnwzvjz3kfu4.cloudfront.net/assets/govuk-frontend-4.7.0.min.css",
            "https://dfnwzvjz3kfu4.cloudfront.net/assets/src/css/main.css",
            "https://d2tm6k52k7dws9.cloudfront.net/assets/govuk-frontend-4.7.0.min.css",
            "https://d2tm6k52k7dws9.cloudfront.net/assets/src/css/main.css",
            # -- p --
            "https://d26l7zu9rvd0xp.cloudfront.net/assets/govuk-frontend-4.7.0.min.css",
            "https://d26l7zu9rvd0xp.cloudfront.net/assets/src/css/main.css",
            "https://cdn.jsdelivr.net/jsdelivr-header.css",
            "https://cdn.jsdelivr.net/npm/universalviewer@4.0.25/dist/uv.min.css",
            "'sha256-aqNNdDLnnrDOnTNdkJpYlAxKVJtLt9CtFLklmInuUAE='",  # pragma: allowlist secret
            "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU='",  # pragma: allowlist secret
            "'sha256-s6M/FyyCCegtJyBnH26lkxb67XZxuZKosiCQWD+VaSo='",  # pragma: allowlist secret
            "'sha256-gNGYzcxL9BKlQFzUxh3BgvhKn2szEIFgg65uQvfaxiI='",  # pragma: allowlist secret
            "'sha256-jcxDeNpsDPUI+dIIqUyA3VBoLgf3Mi2LkRWL/H61who='",  # pragma: allowlist secret
            "'sha256-crS7z4MA9wqqtYsAtmJ6LiW05hz4QJTaokDTQAzc+Hs='",  # pragma: allowlist secret
            "'sha256-8Vn73Z5msbLVngI0nj0OnoRknDpixmr5Qqxqq1oVeyw='",  # pragma: allowlist secret
            "'sha256-1u1O/sNzLBXqLGKzuRbVTI5abqBQBfKsNv3bH5iXOkg='",  # pragma: allowlist secret
            "'sha256-xDT4BUH+7vjNzOH1DSYRS8mdxJbvLVPYsb8hjk4Yccg='",  # pragma: allowlist secret
            "'sha256-JTVvglOxxHXAPZcB40r0wZGNZuFHt0cm0bQVn8LK5GQ='",  # pragma: allowlist secret
            "'sha256-od8NkfAfHOG81BZMpZ608NrC5r2UMOZUuW7MPGF02fU='",  # pragma: allowlist secret
            "'sha256-JTVvglOxxHXAPZcB40r0wZGNZuFHt0cm0bQVn8LK5GQ='",  # pragma: allowlist secret
            "'sha256-7TGyp8O8in/ANC9hFb9GavEXnvRr08lMN/YeRfIcG6w='",  # pragma: allowlist secret
        ]

    @property
    def CSP_IMG_SRC(self):
        return [SELF, self.FLASKS3_CDN_DOMAIN, "data:"]

    @property
    def CSP_FRAME_SRC(self):
        return [SELF, f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com"]

    @property
    def CSP_OBJECT_SRC(self):
        return [SELF, f"https://{self.RECORD_BUCKET_NAME}.s3.amazonaws.com"]

    @property
    def CSP_WORKER_SRC(self):
        return [
            "blob:",
            SELF,
            self.FLASKS3_CDN_DOMAIN,
            "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js",
        ]

    def _get_config_value(self, variable_name):
        pass
