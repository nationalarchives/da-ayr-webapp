from flask import current_app
from sqlalchemy.exc import OperationalError

from app.main.db.models import db
from configs.aws_secrets_manager_config import AWSSecretsManagerConfig

secrets = AWSSecretsManagerConfig()


def execute_with_retry(fn, *args, **kwargs):
    """
    Execute a function that uses the DB, retrying once if password has rotated.
    """
    try:
        return fn(*args, **kwargs)
    except OperationalError as e:
        if "password" in str(e).lower():
            current_app.logger.warning(
                "🔄 Detected invalid DB password — refreshing secret"
            )
            secrets.refresh_db_secret()
            # update URI with fresh secret
            current_app.config["SQLALCHEMY_DATABASE_URI"] = (
                secrets.build_sqlalchemy_uri()
            )
            # dispose of old connections so new ones use the updated URI
            db.engine.dispose()
            return fn(*args, **kwargs)
        raise
