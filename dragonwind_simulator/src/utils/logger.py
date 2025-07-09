"""
DRAGONWIND logging configuration.

This module provides a standardized logging system with colored console output
and file-based logging for the entire simulation platform.
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

# ANSI color codes for terminal output
COLORS = {
    'DEBUG': '\033[36m',  # Cyan
    'INFO': '\033[32m',   # Green
    'WARNING': '\033[33m', # Yellow
    'ERROR': '\033[31m',   # Red
    'CRITICAL': '\033[41m\033[37m', # White on red background
    'RESET': '\033[0m'    # Reset to default
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to log levels for console output."""
    
    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            colored_levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
            record.levelname = colored_levelname
        return super().format(record)


def setup_logger(
    name: str = "dragonwind",
    log_level: int = logging.INFO,
    log_dir: Optional[Union[str, Path]] = None,
    console: bool = True,
    file: bool = True,
    colored_console: bool = True,
) -> logging.Logger:
    """
    Configure and return a logger with console and/or file handlers.
    
    Args:
        name: Logger name
        log_level: Minimum log level to capture
        log_dir: Directory for log files (default: 'logs' in project root)
        console: Whether to enable console output
        file: Whether to enable file output
        colored_console: Whether to enable colored console output
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.handlers = []  # Remove any existing handlers
    
    # Common log format
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        if colored_console:
            console_formatter = ColoredFormatter(log_format, datefmt=date_format)
        else:
            console_formatter = logging.Formatter(log_format, datefmt=date_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if file:
        if not log_dir:
            # Default to 'logs' directory in project root
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "logs"
        
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"dragonwind_{timestamp}.log")
        
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Default logger instance
default_logger = setup_logger()

def get_logger(name: str = "dragonwind") -> logging.Logger:
    """Get a logger with the specified name."""
    if name == "dragonwind":
        return default_logger
    return logging.getLogger(name)
