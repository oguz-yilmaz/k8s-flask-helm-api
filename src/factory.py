import logging
import os
import sys

from dotenv import load_dotenv
from flask import Flask, Response, json
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from src.config.config import Config
from src.core.health import HealthCheck
from src.core.logging import setup_logging
from src.core.metrics import setup_metrics
from src.core.security import configure_security

VERSION = os.getenv("APP_VERSION", "1.0.0")

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
health_check = HealthCheck()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["20000 per day", "5000 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
    # Don't count 429 responses against limit
    default_limits_deduct_when=lambda response: response.status_code != 429,
    default_limits_exempt_when=lambda: False,  # No exemptions
)
logger = logging.getLogger(__name__)

current_env = os.getenv("ENV", "development")
if current_env == "testing":
    config = Config().test_config
elif current_env == "development":
    config = Config().dev_config
else:
    config = Config().production_config


def create_app(config=config):
    load_dotenv()

    app = Flask(__name__)

    app.config["VERSION"] = VERSION

    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    logger.info(f"Starting application in {current_env} environment")

    configure_security(app)

    app.env = config.ENV
    app.secret_key = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Setup health checks
    health_check.setup_health_routes(app)

    # Setup Prometheus metrics
    setup_metrics(app)

    # import models to let the migrate tool know
    from src.core.models.string import String
    from src.core.models.user import User

    register_blueprints(app)

    return app


def register_blueprints(app):
    from flask_swagger_ui import get_swaggerui_blueprint

    from src.api.v1.routes import api
    from src.api.v1.swagger import API_URL, SWAGGER_URL, swagger

    app.register_blueprint(api, url_prefix="/api/v1")

    app.register_blueprint(swagger, url_prefix="/api/v1")
    app.register_blueprint(
        get_swaggerui_blueprint(
            SWAGGER_URL, API_URL, config={"app_name": "Flask String API"}
        ),
        url_prefix=SWAGGER_URL,
    )


app = create_app()
