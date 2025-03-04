import os


class ProductionConfig:
    def __init__(self):
        user = os.getenv("MYSQL_USER", "root")
        host = os.getenv("MYSQL_HOST", "mysql")
        password = os.getenv("MYSQL_PASSWORD", "")
        database = os.getenv("MYSQL_DATABASE", "strings_db")

        self.ENV = "production"
        self.DEBUG = False
        self.PORT = 80
        self.HOST = "0.0.0.0"
        self.SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}?charset=utf8mb4"
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SECRET_KEY = os.getenv("SECRET_KEY", "production-secret-key")
