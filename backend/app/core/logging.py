import logging
import json
import datetime
from typing import Any, Dict

class JSONLogFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for logs.
    """
    def get_log_dict(self, record: logging.LogRecord) -> Dict[str, Any]:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Add any extra attributes passed in the extra dict
        if hasattr(record, "extra_data"):
            log_obj.update(record.extra_data)
            
        return log_obj

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(self.get_log_dict(record))

class CeleryLogHandler(logging.Handler):
    """
    Custom logging handler that sends log records to a Celery task.
    Only activates when Celery worker is available.
    """
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.formatter = JSONLogFormatter()
        self._celery_available = False
        self._write_log_entry = None

    def emit(self, record: logging.LogRecord):
        try:
            # Lazy import and check - only import when actually logging
            if not self._celery_available:
                try:
                    from app.worker import write_log_entry
                    self._write_log_entry = write_log_entry
                    self._celery_available = True
                except ImportError:
                    # Celery not available, skip silently
                    return
            
            if self._celery_available and self._write_log_entry:
                # Prepare log data
                log_data = self.formatter.get_log_dict(record)
                
                # Send to Celery task asynchronously
                # We use delay() to send it to the queue
                self._write_log_entry.delay(log_data)
        except Exception:
            # If Celery is down, we don't want to crash the app or spam errors
            # The StreamHandler will still output the log to console
            # Reset availability flag to retry later
            self._celery_available = False
            self._write_log_entry = None

def setup_logging(level: str = "INFO", enable_celery_logging: bool = True):
    """
    Setup the root logger with JSON formatting.
    
    Args:
        level: Logging level (INFO, DEBUG, etc.)
        enable_celery_logging: Whether to enable Celery log handler (default: True)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplication if re-initialized
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 1. Add StreamHandler (Console) - Always active
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(JSONLogFormatter())
    root_logger.addHandler(stream_handler)

    # 2. Add CeleryLogHandler - Only if enabled and available
    if enable_celery_logging:
        try:
            celery_handler = CeleryLogHandler()
            root_logger.addHandler(celery_handler)
        except Exception as e:
            # If Celery handler fails to initialize, continue without it
            logging.warning(f"Could not initialize Celery log handler: {e}")
    
    # Set levels for some noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger