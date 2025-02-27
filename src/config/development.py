class DevConfig:
    def __init__(self):
        self.ENV = "development"
        self.DEBUG = True
        self.PORT = 5000
        self.HOST = "0.0.0.0"
        # TODO: we can use sqlite with volume for development
        # for fast testing without starting k8s
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SECRET_KEY = "test-secret-key"
