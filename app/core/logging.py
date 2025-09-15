"""
Enhanced logging configuration for the Real Estate API
"""
import logging
import sys
from typing import Any, Dict
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if they exist
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'action'):
            log_entry['action'] = record.action
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO", json_format: bool = True) -> None:
    """Setup logging configuration"""
    
    # Create logger
    logger = logging.getLogger("real_estate_api")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Set formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get logger instance"""
    if name:
        return logging.getLogger(f"real_estate_api.{name}")
    return logging.getLogger("real_estate_api")


class LoggerMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__)
    
    def log_action(self, action: str, **kwargs) -> None:
        """Log an action with additional context"""
        extra = {
            'action': action,
            **kwargs
        }
        self.logger.info(f"Action: {action}", extra=extra)
    
    def log_error(self, error: Exception, action: str = None, **kwargs) -> None:
        """Log an error with context"""
        extra = {
            'action': action,
            'error_type': type(error).__name__,
            **kwargs
        }
        self.logger.error(f"Error: {str(error)}", extra=extra, exc_info=True)

