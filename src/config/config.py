from src.config.development import DevConfig
from src.config.production import ProductionConfig
from src.config.testing import TestConfig


class Config:
    def __init__(self):
        self.dev_config = DevConfig()
        self.production_config = ProductionConfig()
        self.test_config = TestConfig()
