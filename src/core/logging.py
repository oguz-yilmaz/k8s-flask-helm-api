import json
import logging
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Simple JSON formatter for logs"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        if record.exc_info:
            log_data["exception"] = str(record.exc_info[1])

        # Add custom fields
        for key, value in record.__dict__.items():
            if key.startswith("_") and not key.startswith("__"):
                log_data[key[1:]] = value

        return json.dumps(log_data)


def setup_logging(log_level="INFO"):
    """Configure application logging with JSON format"""
    root_logger = logging.getLogger()

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)

    return root_logger
