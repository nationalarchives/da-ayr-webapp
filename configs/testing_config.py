from configs.local_config import LocalConfig


class TestingConfig(LocalConfig):
    TESTING = True
    SECRET_KEY = "TEST_SECRET_KEY"  # pragma: allowlist secret
    WTF_CSRF_ENABLED = False
