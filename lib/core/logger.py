import logging
import os
from logging import handlers

import structlog


LOG_ROTATE_WHEN = os.getenv(key="LOG_ROTATE_WHEN", default="W6")
LOG_ROTATE_BACKUP = int(os.getenv(key="LOG_ROTATE_BACKUP", default="4"))


def initialize_logger():
    # Configure standard logger to log to a rotating file
    log_file_path = "logs/rest_server.log"
    file_handler = handlers.TimedRotatingFileHandler(
        filename=log_file_path,
        when=LOG_ROTATE_WHEN,
        backupCount=LOG_ROTATE_BACKUP,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=[file_handler],
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.AsyncBoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
