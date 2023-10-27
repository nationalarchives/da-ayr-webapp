from config import Config


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
