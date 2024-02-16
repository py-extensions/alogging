import logging

from . import handlers
from .logger import AsyncLogger, basicConfig, getLogger

Formatter = logging.Formatter
LogRecord = logging.LogRecord

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

start_backend = AsyncLogger.start_backend


__all__ = [
    "getLogger",
    "handlers",
    "basicConfig",
    "Formatter",
    "LogRecord",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "start_backend",
]
