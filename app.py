import os

from flask_migrate import upgrade

from src import app, config

if __name__ == "__main__":
    os.environ["ENV"] = "testing"
    with app.app_context():
        # For in-memory SQLite, run migrations automatically
        if config.SQLALCHEMY_DATABASE_URI == "sqlite:///:memory:":
            print("Running migrations for in-memory database...")

            basedir = os.path.abspath(os.path.dirname(__file__))
            upgrade(os.path.join(basedir, "migrations"))

            print("Migrations complete!")

    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
