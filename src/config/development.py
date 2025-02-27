import os


class DevConfig:
    def __init__(self):
        user = os.getenv("MYSQL_USER", "root")
        host = os.getenv("MYSQL_HOST", "mysql")
        password = os.getenv("MYSQL_PASSWORD", "")
        database = os.getenv("MYSQL_DATABASE", "strings_db")

        self.ENV = "development"
        self.DEBUG = True
        self.PORT = 5000
        self.HOST = "0.0.0.0"
        self.SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SECRET_KEY = "test-secret-key"
