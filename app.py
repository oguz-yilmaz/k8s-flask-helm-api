import os

from flask_migrate import upgrade

from src import app, config


def migrate():
    with app.app_context():
        if config.SQLALCHEMY_DATABASE_URI == "sqlite:///:memory:":
            print("Running migrations for in-memory database...")

            basedir = os.path.abspath(os.path.dirname(__file__))
            upgrade(os.path.join(basedir, "migrations"))

            print("Migrations complete!")


if os.environ.get("ENV") == "testing":
    migrate()

if __name__ == "__main__":
    os.environ["ENV"] = "testing"

    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
