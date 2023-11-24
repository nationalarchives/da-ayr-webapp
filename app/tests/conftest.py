import pytest

from app import create_app
from configs.testing_config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    yield app


@pytest.fixture
def client(app):
    yield app.test_client()
