import pytest
from testing.postgresql import PostgresqlFactory

from app import create_app
from configs.testing_config import TestingConfig


@pytest.fixture
def app(database):
    app = create_app(TestingConfig, database.url())
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture()
def database(request):
    # Launch new PostgreSQL server
    postgresql = PostgresqlFactory(cache_initialized_db=True)()
    yield postgresql

    # PostgreSQL server is terminated here
    @request.addfinalizer
    def drop_database():
        postgresql.stop()
