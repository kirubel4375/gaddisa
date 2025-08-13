#!/usr/bin/env python3
"""
Language Debug Logging Configuration
===================================

This module provides comprehensive logging for language preference operations
in the Emergency Bot system. It tracks all language changes, database operations,
and error conditions to help debug language preference issues.

Usage:
    from language_debug_logging import setup_language_logging, get_language_logger
    
    # Set up logging (call once at startup)
    setup_language_logging()
    
    # Get logger for use in modules
    logger = get_language_logger(__name__)
    logger.info("Language operation started")
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
LANGUAGE_LOG_FILE = LOGS_DIR / "language_operations.log"
ERROR_LOG_FILE = LOGS_DIR / "language_errors.log"
DEBUG_LOG_FILE = LOGS_DIR / "language_debug.log"

class LanguageDebugFormatter(logging.Formatter):
    """Custom formatter for language debug logging with enhanced context"""
    
    def format(self, record):
        # Add timestamp with microseconds
        record.precise_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Add process and thread info
        record.process_thread = f"PID:{os.getpid()}-TID:{record.thread}"
        
        # Enhanced format with more context
        format_string = (
            "[{precise_time}] [{levelname:8}] "
            "[{process_thread}] [{name}:{lineno}] "
            "[FUNC:{funcName}] {message}"
        )
        
        formatter = logging.Formatter(format_string, style='{')
        return formatter.format(record)

def setup_language_logging(log_level=logging.DEBUG):
    """
    Set up comprehensive logging for language operations
    
    Creates three log files:
    1. language_operations.log - All language-related operations (INFO+)
    2. language_errors.log - Only errors and critical issues (ERROR+)
    3. language_debug.log - Detailed debug information (DEBUG+)
    """
    
    # Create custom logger for language operations
    language_logger = logging.getLogger('language_ops')
    language_logger.setLevel(log_level)
    
    # Prevent duplicate logs if already configured
    if language_logger.handlers:
        return language_logger
    
    # Create custom formatter
    formatter = LanguageDebugFormatter()
    
    # 1. Operations log file handler (INFO and above)
    ops_handler = logging.handlers.RotatingFileHandler(
        LANGUAGE_LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    ops_handler.setLevel(logging.INFO)
    ops_handler.setFormatter(formatter)
    
    # 2. Error log file handler (ERROR and above)
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # 3. Debug log file handler (DEBUG and above)
    debug_handler = logging.handlers.RotatingFileHandler(
        DEBUG_LOG_FILE,
        maxBytes=20*1024*1024,  # 20MB
        backupCount=3,
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    
    # 4. Console handler for immediate feedback (WARNING and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    
    # Add all handlers to the logger
    language_logger.addHandler(ops_handler)
    language_logger.addHandler(error_handler)
    language_logger.addHandler(debug_handler)
    language_logger.addHandler(console_handler)
    
    # Log initialization
    language_logger.info("=" * 80)
    language_logger.info("LANGUAGE DEBUG LOGGING INITIALIZED")
    language_logger.info(f"Operations log: {LANGUAGE_LOG_FILE}")
    language_logger.info(f"Error log: {ERROR_LOG_FILE}")
    language_logger.info(f"Debug log: {DEBUG_LOG_FILE}")
    language_logger.info("=" * 80)
    
    return language_logger

def get_language_logger(name=None):
    """
    Get a logger instance for language operations
    
    Args:
        name: Logger name (usually __name__ from calling module)
    
    Returns:
        Logger instance configured for language operations
    """
    if name:
        return logging.getLogger(f'language_ops.{name}')
    else:
        return logging.getLogger('language_ops')

def log_language_operation(func):
    """
    Decorator to automatically log language operations with detailed context
    
    Usage:
        @log_language_operation
        def update_user_language(user_id, language_code):
            # function implementation
    """
    def wrapper(*args, **kwargs):
        logger = get_language_logger(func.__module__)
        
        # Log function entry
        logger.debug(f"ENTERING {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Log successful completion
            logger.info(f"SUCCESS {func.__name__} returned: {result}")
            return result
            
        except Exception as e:
            # Log error with full traceback
            logger.error(f"ERROR in {func.__name__}: {str(e)}", exc_info=True)
            raise
    
    return wrapper

def log_user_language_change(user_id, old_language, new_language, success=True, error_msg=None):
    """
    Log language change events with detailed context
    
    Args:
        user_id: Telegram user ID
        old_language: Previous language code
        new_language: New language code
        success: Whether the change was successful
        error_msg: Error message if unsuccessful
    """
    logger = get_language_logger('language_change')
    
    if success:
        logger.info(
            f"LANGUAGE_CHANGE_SUCCESS: User {user_id} changed from '{old_language}' to '{new_language}'"
        )
    else:
        logger.error(
            f"LANGUAGE_CHANGE_FAILED: User {user_id} failed to change from '{old_language}' to '{new_language}' - {error_msg}"
        )

def log_database_operation(operation, table, user_id, fields=None, success=True, error_msg=None):
    """
    Log database operations related to language preferences
    
    Args:
        operation: Type of operation (SELECT, UPDATE, INSERT, etc.)
        table: Database table name
        user_id: User identifier
        fields: Fields being operated on
        success: Whether operation was successful
        error_msg: Error message if unsuccessful
    """
    logger = get_language_logger('database')
    
    fields_str = f" fields={fields}" if fields else ""
    
    if success:
        logger.debug(
            f"DB_{operation}_SUCCESS: {table} for user {user_id}{fields_str}"
        )
    else:
        logger.error(
            f"DB_{operation}_FAILED: {table} for user {user_id}{fields_str} - {error_msg}"
        )

def create_debug_summary():
    """
    Create a summary of recent language operation logs for troubleshooting
    
    Returns:
        String containing summary of recent language operations
    """
    try:
        summary_lines = []
        summary_lines.append("LANGUAGE DEBUG SUMMARY")
        summary_lines.append("=" * 50)
        summary_lines.append(f"Generated at: {datetime.now()}")
        summary_lines.append("")
        
        # Check if log files exist and get recent entries
        for log_file, description in [
            (LANGUAGE_LOG_FILE, "Recent Operations"),
            (ERROR_LOG_FILE, "Recent Errors"),
        ]:
            summary_lines.append(f"{description} ({log_file.name}):")
            summary_lines.append("-" * 30)
            
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # Get last 10 lines
                        recent_lines = lines[-10:] if len(lines) > 10 else lines
                        for line in recent_lines:
                            summary_lines.append(line.rstrip())
                except Exception as e:
                    summary_lines.append(f"Error reading {log_file}: {e}")
            else:
                summary_lines.append("Log file does not exist")
            
            summary_lines.append("")
        
        return "\n".join(summary_lines)
        
    except Exception as e:
        return f"Error creating debug summary: {e}"

if __name__ == "__main__":
    # Test the logging system
    setup_language_logging()
    logger = get_language_logger(__name__)
    
    logger.info("Testing language logging system")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test logging functions
    log_user_language_change("123456", "en", "am", success=True)
    log_user_language_change("123456", "am", "om", success=False, error_msg="Database connection failed")
    log_database_operation("UPDATE", "UserProfile", "123456", ["language"], success=True)
    
    print("\nDebug Summary:")
    print(create_debug_summary())