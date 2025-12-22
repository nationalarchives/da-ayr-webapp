from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.main.db.models import db
from configs.aws_secrets_manager_config import AWSSecretsManagerConfig

secrets = AWSSecretsManagerConfig()


def execute_with_retry(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)

    except OperationalError as e:
        if "password" not in str(e).lower():
            raise

        current_app.logger.warning(
            "🔄 Detected invalid DB password — refreshing secret"
        )

        # 1. Refresh secret
        secrets.refresh_db_secret()
        new_uri = secrets.build_sqlalchemy_uri()

        # 2. Update Flask config
        current_app.config["SQLALCHEMY_DATABASE_URI"] = new_uri

        # 3. Dispose ALL existing connections
        db.engine.dispose()

        # 4. Create a new engine
        new_engine = create_engine(
            new_uri,
            pool_pre_ping=True,
            pool_recycle=300,
        )

        # 5. Rebind Flask-SQLAlchemy
        db.engines[current_app] = new_engine

        # 6. Reset session state
        db.session.remove()

        current_app.logger.warning(
            "✅ Database engine rebound with refreshed secret"
        )

        return fn(*args, **kwargs)
