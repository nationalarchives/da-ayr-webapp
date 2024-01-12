from unittest.mock import patch

import pytest
from flask.testing import FlaskClient
from testing.postgresql import PostgresqlFactory

from app import create_app
from app.main.authorize.ayr_user import AYRUser
from app.main.db.models import Body, db
from app.tests.factories import BodyFactory
from configs.testing_config import TestingConfig


@pytest.fixture(scope="function")
def mock_standard_user():
    patcher = patch("app.main.authorize.ayr_user.AYRUser.from_access_token")

    def _mock_standard_user(client: FlaskClient, body: str = "test_body"):
        mock_ayr_user_from_access_token = patcher.start()
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        groups = ["/ayr_user_type/view_dept", f"/transferring_body_user/{body}"]

        mock_ayr_user_from_access_token.return_value = AYRUser(groups)

        if Body.query.filter(Body.Name == body).count() == 0:
            BodyFactory(Name=body)

    yield _mock_standard_user

    patcher.stop()


@pytest.fixture(scope="function")
def mock_superuser():
    patcher = patch("app.main.authorize.ayr_user.AYRUser.from_access_token")

    def _mock_superuser(client: FlaskClient):
        mock_ayr_user_from_access_token = patcher.start()
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        mock_ayr_user_from_access_token.return_value = AYRUser(
            ["/ayr_user_type/view_all"]
        )

    yield _mock_superuser

    patcher.stop()


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
