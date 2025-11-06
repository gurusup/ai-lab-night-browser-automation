"""Logging configuration using structlog."""

import sys
from typing import Any

import structlog
from structlog.typing import EventDict, Processor

from .config import config


def add_timestamp(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add timestamp to log events."""
    import datetime

    event_dict["timestamp"] = datetime.datetime.now().isoformat()
    return event_dict


def configure_logging() -> None:
    """Configure structlog for the application."""
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        add_timestamp,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
    ]

    # Add appropriate renderer based on environment
    if sys.stderr.isatty():
        # Pretty console output for development
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.processors, config.mcp_log_level.upper(), 20)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """
    Get a configured logger instance.

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        Configured structlog logger
    """
    configure_logging()
    return structlog.get_logger(name)
