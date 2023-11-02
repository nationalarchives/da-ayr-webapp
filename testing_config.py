from config import Config


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "TEST_SECRET_KEY"  # pragma: allowlist secret
    WTF_CSRF_ENABLED = False
