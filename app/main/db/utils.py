from flask import current_app
from sqlalchemy.exc import OperationalError

from app.main.db.models import db
from configs.aws_secrets_manager_config import AWSSecretsManagerConfig

secrets = AWSSecretsManagerConfig()


def execute_with_retry(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except OperationalError as e:
        if "password" in str(e).lower():
            current_app.logger.warning(
                "🔄 Detected invalid DB password — refreshing secret"
            )
            secrets.refresh_db_secret()
            # update URI with fresh secret
            new_uri = secrets.build_sqlalchemy_uri()
            current_app.logger.warning(f"Old URI = {new_uri}")
            current_app.config["SQLALCHEMY_DATABASE_URI"] = new_uri
            current_app.logger.warning(f"NEW URI = {new_uri}")
            # dispose old engine and rebuild with new URI
            db.engine.dispose()
            db.session.remove()

            return fn(*args, **kwargs)
        raise
