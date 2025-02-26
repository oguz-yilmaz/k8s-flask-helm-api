import os

from dotenv import load_dotenv
from flask import Flask, Response, json
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from src.config.config import Config

# loading environment variables
load_dotenv()

# declaring flask application
app = Flask(__name__)

# calling the dev configuration
config = Config().dev_config

# calling the production configuration
# config = Config().production_config

# making our application to use dev env
app.env = config.ENV

# load the secret key defined in the .env file
app.secret_key = os.environ.get("SECRET_KEY")
bcrypt = Bcrypt(app)

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

# sql alchemy instance
db = SQLAlchemy(app)

# Flask Migrate instance to handle migrations
migrate = Migrate(app, db)

# import api blueprint to register it with app
from src.api.v1.routes import api

# import models to let the migrate tool know
from src.core.models.string import String
from src.core.models.user import User

app.register_blueprint(api, url_prefix="/api/v1")


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


from flask_swagger_ui import get_swaggerui_blueprint

from src.api.v1.swagger import API_URL, SWAGGER_URL, swagger

# Add after registering your API blueprint:
app.register_blueprint(swagger, url_prefix="/api/v1")
app.register_blueprint(
    get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={"app_name": "Flask String API"}
    ),
    url_prefix=SWAGGER_URL,
)
