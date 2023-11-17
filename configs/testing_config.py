from configs.base_config import BaseConfig


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "TEST_SECRET_KEY"  # pragma: allowlist secret
    WTF_CSRF_ENABLED = False

    def _get_config_value(self, variable_name):
        return ""
