from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.main.db.models import db
from configs.aws_secrets_manager_config import AWSSecretsManagerConfig


def rebuild_engine(new_uri: str):
    """
    Safely rebuild SQLAlchemy engine with fresh credentials.
    """
    db.session.remove()
    db.engine.dispose()

    engine = create_engine(
        new_uri,
        pool_pre_ping=True,
        pool_recycle=300,
    )

    db._engine = engine


def execute_with_retry(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)

    except OperationalError as e:
        if "password" not in str(e).lower():
            raise

        current_app.logger.warning(
            "🔄 Detected invalid DB password — refreshing secret"
        )

        secrets = AWSSecretsManagerConfig()
        secrets.refresh_db_secret()

        new_uri = secrets.build_sqlalchemy_uri()
        current_app.config["SQLALCHEMY_DATABASE_URI"] = new_uri

        rebuild_engine(new_uri)

        return fn(*args, **kwargs)
