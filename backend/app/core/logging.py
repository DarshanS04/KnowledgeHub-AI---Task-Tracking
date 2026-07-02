import logging
import sys
import time
from typing import Any, Dict
import json
from app.config import settings

# Global context to hold request-scoped information like request_id
import contextvars
request_id_ctx_var = contextvars.ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    """
    Custom formatter to log messages as JSON structured strings,
    including metadata like timestamp, level, name, request_id, etc.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S") + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "file": f"{record.pathname}:{record.lineno}",
            "request_id": request_id_ctx_var.get()
        }

        # Include traceback details if an exception is logged
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging() -> None:
    """
    Initializes structured logging system. Prints standard log messages or 
    JSON messages depending on the current environment settings.
    """
    root_logger = logging.getLogger()
    
    # Set level based on environment
    log_level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO
    root_logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # In production, use JSON format. In development, use human-readable or JSON.
    if settings.ENVIRONMENT == "production":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
        )
    
    console_handler.setFormatter(formatter)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    root_logger.addHandler(console_handler)

    # Set external libraries log levels to avoid clutter
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client").setLevel(logging.WARNING)
