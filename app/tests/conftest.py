import pytest
from testing.postgresql import PostgresqlFactory

from app import create_app
from app.main.db.models import db
from configs.testing_config import TestingConfig


@pytest.fixture()
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
