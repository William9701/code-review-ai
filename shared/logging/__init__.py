"""
Logging shared module
"""
from .logger import (
    setup_logging,
    get_logger,
    get_logger_with_context,
    LoggerAdapter
)

__all__ = [
    "setup_logging",
    "get_logger",
    "get_logger_with_context",
    "LoggerAdapter"
]
