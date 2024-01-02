from unittest.mock import patch

import pytest
from flask.testing import FlaskClient
from testing.postgresql import PostgresqlFactory

from app import create_app
from app.main.db.models import db
from configs.testing_config import TestingConfig


def mock_standard_user(client: FlaskClient, body: str):
    with client.session_transaction() as session:
        session["access_token"] = "valid_token"

    groups = [
        "/ayr_user_type/view_department",
        f"/transferring_body_user/{body}",
    ]

    patcher = patch("app.main.authorize.permissions_helpers.get_user_groups")
    mock_get_user_groups = patcher.start()
    mock_get_user_groups.return_value = groups


def mock_superuser(client: FlaskClient):
    with client.session_transaction() as session:
        session["access_token"] = "valid_token"

    patcher = patch("app.main.authorize.permissions_helpers.get_user_groups")
    mock_get_user_groups = patcher.start()
    mock_get_user_groups.return_value = ["/ayr_user_type/view_all"]


@pytest.fixture
def app(database):
    app = create_app(TestingConfig, database.url())
    yield app


@pytest.fixture(scope="function")
def client(app):
    db.session.remove()
    db.drop_all()
    db.create_all()
    yield app.test_client()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "ignore_https_errors": True}


@pytest.fixture(scope="session")
def database(request):
    # Launch new PostgreSQL server
    postgresql = PostgresqlFactory(cache_initialized_db=True)()
    yield postgresql

    # PostgreSQL server is terminated here
    @request.addfinalizer
    def drop_database():
        postgresql.stop()
