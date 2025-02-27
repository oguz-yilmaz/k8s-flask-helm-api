import pytest
from flask import Flask
from src.core.security import configure_security
from src.config.dev_config import DevConfig
from src.api.v1.controllers.strings_controller import strings
from src.api.v1.controllers.auth_controller import users
from src import app

@pytest.fixture(scope='session')
def dev_config():
    return DevConfig()

@pytest.fixture(scope='session')
def base_url(dev_config):
    return f"http://{dev_config.HOST}:{dev_config.PORT}"

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()
