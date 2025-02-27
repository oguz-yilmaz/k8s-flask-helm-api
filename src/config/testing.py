class TestConfig:
    def __init__(self):
        self.ENV = "testing"
        self.DEBUG = True
        self.PORT = 5000
        self.HOST = "0.0.0.0"
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SECRET_KEY = "test-secret-key"
