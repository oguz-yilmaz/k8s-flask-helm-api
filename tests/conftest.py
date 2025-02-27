import os

import pytest
from flask import Flask

from src import app
from src.config.testing import TestConfig
from src.factory import create_app, db


@pytest.fixture(scope="session")
def app_with_db():
    os.environ["ENV"] = "test"

    test_app = create_app(TestConfig())

    with test_app.app_context():
        db.create_all()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app_with_db):
    with app_with_db.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def session(app_with_db):
    """Provides a database session for tests"""
    with app_with_db.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        session = db.session

        yield session

        # Rollback the transaction after the test is done
        session.close()
        transaction.rollback()
        connection.close()
