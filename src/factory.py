import os

from dotenv import load_dotenv
from flask import Flask, Response, json
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from src.config.config import Config
from src.core.security import configure_security

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

current_env = os.getenv("ENV", "dev")
config = Config().dev_config if current_env == "dev" else Config().production_config


def create_app():
    # loading environment variables
    load_dotenv()

    # declaring flask application
    app = Flask(__name__)

    configure_security(app)

    app.env = config.ENV

    # load the secret key defined in the .env file
    app.secret_key = os.environ.get("SECRET_KEY")

    # # Configure logging
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    #     handlers=[logging.StreamHandler(sys.stdout)],
    # )
    # logger = logging.getLogger(__name__)

    # Database Configuration
    host = os.getenv("MYSQL_HOST", "mysql")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "strings_db")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # import models to let the migrate tool know
    from src.core.models.string import String
    from src.core.models.user import User

    register_blueprints(app)

    @app.route("/health", methods=["GET"])
    def health_check():
        return Response(
            response=json.dumps({"status": "healthy"}),
            status=200,
            mimetype="application/json",
        )

    @app.route("/ready", methods=["GET"])
    def ready_check():
        return Response(
            response=json.dumps({"status": "ready"}),
            status=200,
            mimetype="application/json",
        )

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
