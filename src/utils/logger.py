"""Logging configuration and utilities."""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..config.constants import LOG_FILE, APP_NAME


class Logger:
    """Application logger with file and console output."""
    
    _instance: Optional["Logger"] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Configure logging with file and console handlers."""
        self._logger = logging.getLogger(APP_NAME)
        self._logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self._logger.handlers:
            return
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # File handler
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to create log file: {e}")
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        if self._logger:
            self._logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        if self._logger:
            self._logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        if self._logger:
            self._logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False) -> None:
        """Log error message."""
        if self._logger:
            self._logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False) -> None:
        """Log critical message."""
        if self._logger:
            self._logger.critical(message, exc_info=exc_info)
    
    def exception(self, message: str) -> None:
        """Log exception with traceback."""
        if self._logger:
            self._logger.exception(message)


# Global logger instance
logger = Logger()
