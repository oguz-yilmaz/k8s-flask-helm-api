from flask import Blueprint

from src.api.v1.controllers.auth_controller import users
from src.api.v1.controllers.strings_controller import strings

api = Blueprint("api", __name__)

api.register_blueprint(strings, url_prefix="/strings")
api.register_blueprint(users, url_prefix="/auth")

