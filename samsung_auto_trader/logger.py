"""
Structured logging for Samsung Auto Trader.

Provides a centralized logging interface with consistent formatting
for all modules.
"""

import logging
import sys
from typing import Optional

import config


def setup_logger(name: str) -> logging.Logger:
    """
    Set up and return a logger instance with consistent formatting.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Set logging level
    logger.setLevel(config.LOG_LEVEL)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(config.LOG_LEVEL)
    
    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


# Helper functions for common logging patterns
def log_api_call(logger: logging.Logger, method: str, url: str, params: Optional[dict] = None) -> None:
    """Log API call details."""
    logger.debug(f"📡 API {method} {url}")
    if params:
        logger.debug(f"   Parameters: {params}")


def log_api_response(logger: logging.Logger, status_code: int, is_success: bool, message: str = "") -> None:
    """Log API response."""
    icon = "✅" if is_success else "❌"
    logger.info(f"{icon} API Response: {status_code} - {message}")


def log_trading_action(logger: logging.Logger, action: str, details: str) -> None:
    """Log trading actions (buy, sell, check balance)."""
    logger.info(f"🔄 {action}: {details}")


def log_error(logger: logging.Logger, error_type: str, message: str, exception: Optional[Exception] = None) -> None:
    """Log errors with optional exception details."""
    logger.error(f"⚠️  {error_type}: {message}")
    if exception:
        logger.debug(f"Exception details: {exception}", exc_info=True)


def log_token_management(logger: logging.Logger, action: str, details: str) -> None:
    """Log token-related activities (issued, cached, reused, expired)."""
    logger.info(f"🔐 Token {action}: {details}")


def log_trading_window(logger: logging.Logger, is_open: bool, current_time: str) -> None:
    """Log trading window status."""
    icon = "🟢" if is_open else "🔴"
    logger.info(f"{icon} Trading window at {current_time}: {'OPEN ✅' if is_open else 'CLOSED ❌'}")
