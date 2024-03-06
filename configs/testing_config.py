from configs.base_config import BaseConfig


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "TEST_SECRET_KEY"  # pragma: allowlist secret
    DEFAULT_PAGE_SIZE = 5
    DEFAULT_DATE_FORMAT = "DD/MM/YYYY"

    def _get_config_value(self, variable_name):
        return ""
