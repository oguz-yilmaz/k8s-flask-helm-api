from src import app, config

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


# -----------------------------------------------------------------------------------------
# --------------------------------- OLD app.py --------------------------------------------
# -----------------------------------------------------------------------------------------
# import logging
# import os
# import random
# import sys

# from flask import Flask, jsonify, request
# from flask_migrate import Migrate
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[logging.StreamHandler(sys.stdout)],
# )
# logger = logging.getLogger(__name__)

# # Database Configuration
# host = os.getenv("MYSQL_HOST", "mysql")
# user = os.getenv("MYSQL_USER", "root")
# password = os.getenv("MYSQL_PASSWORD", "")
# database = os.getenv("MYSQL_DATABASE", "strings_db")

# app.config["SQLALCHEMY_DATABASE_URI"] = (
#     f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
# )
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# # Initialize SQLAlchemy
# db = SQLAlchemy(app)

# # Initialize Flask-Migrate
# migrate = Migrate(app, db)


# # Define Models
# class String(db.Model):
#     __tablename__ = "strings"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     value = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())


# # Routes
# @app.route("/health", methods=["GET"])
# def health_check():
#     return jsonify({"status": "healthy"}), 200


# @app.route("/ready", methods=["GET"])
# def ready_check():
#     return jsonify({"status": "ready"}), 200


# @app.route("/api/save", methods=["POST"])
# def save_string():
#     try:
#         data = request.get_json()
#         if not data or "string" not in data:
#             return jsonify({"error": "No string provided"}), 400

#         input_string = data["string"]

#         # Create a new String object
#         new_string = String(value=input_string)
#         db.session.add(new_string)
#         db.session.commit()

#         return jsonify({"message": "String saved successfully"}), 201

#     except Exception as e:
#         logger.error(f"Error saving string: {e}")
#         return jsonify({"error": str(e)}), 500


# @app.route("/api/random", methods=["GET"])
# def get_random_string():
#     try:
#         count = db.session.query(String).count()

#         if count == 0:
#             return jsonify({"message": "No strings found"}), 404

#         # Get a random string
#         random_offset = random.randint(0, count - 1)
#         random_string = db.session.query(String).offset(random_offset).first()

#         return jsonify({"random_string": random_string.value}), 200

#     except Exception as e:
#         logger.error(f"Error getting random string: {e}")
#         return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
