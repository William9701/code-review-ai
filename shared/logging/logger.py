"""
Centralized logging configuration
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for structured logging
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """
        Add custom fields to log record

        Args:
            log_record: Log record dictionary
            record: Original log record
            message_dict: Message dictionary
        """
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        log_record["timestamp"] = datetime.utcnow().isoformat()

        # Add service info
        log_record["service"] = os.getenv("SERVICE_NAME", "unknown")
        log_record["environment"] = os.getenv("ENVIRONMENT", "development")

        # Add level
        log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add execution info
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add trace ID if available (for distributed tracing)
        if hasattr(record, "trace_id"):
            log_record["trace_id"] = record.trace_id

        # Add request ID if available
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id


def setup_logging(
    level: str = None, service_name: str = None, json_logs: bool = True
) -> logging.Logger:
    """
    Setup centralized logging configuration

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        service_name: Service name for log identification
        json_logs: Use JSON format for logs (default: True)

    Returns:
        Configured root logger
    """
    # Get log level from env or parameter
    log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()

    # Set service name
    if service_name:
        os.environ["SERVICE_NAME"] = service_name

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers = []

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Set formatter based on json_logs flag
    if json_logs:
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(service)s %(logger)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Log initial message
    root_logger.info(
        f"Logging configured",
        extra={
            "level": log_level,
            "service": os.getenv("SERVICE_NAME", "unknown"),
            "json_logs": json_logs,
        },
    )

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger for specific module

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter for adding contextual information
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message to add context

        Args:
            msg: Log message
            kwargs: Keyword arguments

        Returns:
            Tuple of (msg, kwargs)
        """
        # Add extra context
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        kwargs["extra"].update(self.extra)
        return msg, kwargs


def get_logger_with_context(name: str, **context) -> LoggerAdapter:
    """
    Get logger with additional context

    Args:
        name: Logger name
        **context: Additional context fields

    Returns:
        Logger adapter with context

    Usage:
        logger = get_logger_with_context(
            __name__,
            request_id="abc123",
            user_id="user456"
        )
        logger.info("Processing request")
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)
