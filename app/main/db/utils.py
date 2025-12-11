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
            print("🔄 Detected invalid DB password — refreshing secret")
            secrets.refresh_db_secret()
            db.engine.dispose()
            db.app.config["SQLALCHEMY_DATABASE_URI"] = (
                secrets.build_sqlalchemy_uri()
            )
            # rebuild engine with new URI
            db.init_app(db.app)
            return fn(*args, **kwargs)
        raise
