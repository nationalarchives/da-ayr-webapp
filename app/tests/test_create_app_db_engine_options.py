from app import create_app, get_connection
from configs.testing_config import TestingConfig


def test_create_app_non_local_env_uses_pool_pre_ping():
    """
    GIVEN a non-local environment (e.g. Lambda behind RDS Proxy)
    WHEN create_app is called with local_env=False
    THEN the SQLAlchemy engine options should enable pool_pre_ping, so stale
        pooled connections are detected and discarded rather than reused
    """
    app = create_app(TestingConfig, False)

    engine_options = app.config["SQLALCHEMY_ENGINE_OPTIONS"]

    assert engine_options["pool_pre_ping"] is True
    assert engine_options["creator"] is get_connection
