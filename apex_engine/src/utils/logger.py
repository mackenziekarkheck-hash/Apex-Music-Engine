"""
APEX Engine Logger - Hierarchical Context Logging with Trace IDs.

Provides structured logging with:
- Unique trace IDs for request tracking
- Agent-specific log contexts
- Performance timing
- Log level management
"""

import logging
import sys
import uuid
from typing import Optional
from functools import wraps
from datetime import datetime
import threading


_trace_id_local = threading.local()


def get_trace_id() -> str:
    """Get the current trace ID for this thread."""
    if not hasattr(_trace_id_local, 'trace_id'):
        _trace_id_local.trace_id = str(uuid.uuid4())[:8]
    return _trace_id_local.trace_id


def set_trace_id(trace_id: Optional[str] = None):
    """Set a new trace ID for this thread."""
    _trace_id_local.trace_id = trace_id or str(uuid.uuid4())[:8]


class APEXFormatter(logging.Formatter):
    """Custom formatter with trace ID and context."""
    
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m'
    }
    
    def __init__(self, use_color: bool = True):
        super().__init__()
        self.use_color = use_color
    
    def format(self, record: logging.LogRecord) -> str:
        trace_id = get_trace_id()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        if self.use_color and sys.stdout.isatty():
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            level_str = f"{color}{record.levelname:8}{reset}"
        else:
            level_str = f"{record.levelname:8}"
        
        name = record.name.replace('apex.', '').upper()
        if len(name) > 15:
            name = name[:15]
        
        return f"[{timestamp}] [{trace_id}] [{name:15}] {level_str} | {record.getMessage()}"


def setup_logger(
    name: str = "apex",
    level: int = logging.INFO,
    use_color: bool = True
) -> logging.Logger:
    """
    Setup and configure the APEX logger.
    
    Args:
        name: Logger name
        level: Logging level
        use_color: Whether to use colored output
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(APEXFormatter(use_color=use_color))
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific component.
    
    Args:
        name: Component name (e.g., 'orchestrator', 'lyrical_architect')
        
    Returns:
        Logger instance with proper hierarchy
    """
    full_name = f"apex.{name}" if not name.startswith("apex.") else name
    
    parent = logging.getLogger("apex")
    if not parent.handlers:
        setup_logger()
    
    return logging.getLogger(full_name)


def log_execution(func):
    """Decorator to log function execution with timing."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = func.__qualname__
        
        logger.debug(f"Starting {func_name}")
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            logger.debug(f"Completed {func_name} in {elapsed:.2f}ms")
            return result
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Failed {func_name} after {elapsed:.2f}ms: {e}")
            raise
    
    return wrapper


class LogContext:
    """Context manager for temporary log context."""
    
    def __init__(self, trace_id: Optional[str] = None, **context):
        self.new_trace_id = trace_id or str(uuid.uuid4())[:8]
        self.old_trace_id = None
        self.context = context
    
    def __enter__(self):
        self.old_trace_id = get_trace_id()
        set_trace_id(self.new_trace_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        set_trace_id(self.old_trace_id)
        return False
