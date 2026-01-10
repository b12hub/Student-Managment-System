import logging
import os
import functools
from datetime import datetime

# Setup loggers
# We need two logs: logs/system.log and logs/security.log
# I will set them up at module level, but safely.

def _setup_logger(name, log_file, level=logging.INFO):
    """Function to setup as many loggers as you want"""
    # Create directory if it doesn't exist.
    # Relative path "logs/" required.
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    handler = logging.FileHandler(log_file)        
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Avoid adding multiple handlers if re-imported
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

# Configure loggers
# Assuming the script runs from root, relative path should be 'logs/system.log'
# But if it runs from elsewhere, this might be tricky.
# Prompt says: "No hardcoded paths (use relative paths)."
# I will use 'logs/...' relative to CWD.

system_logger = _setup_logger('system_logger', 'logs/system.log')
security_logger = _setup_logger('security_logger', 'logs/security.log')

def log_action(action_name: str):
    """
    Decorator to log actions.
    Logs to system.log and security.log (for failures).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user_id = "Unknown"
            if 'current_user' in kwargs:
                user = kwargs['current_user']
                # Try to get ID, attribute name might vary but typically 'id' or 'user_id'
                # Prompt says: "user ID (if provided)"
                if hasattr(user, 'id'):
                    user_id = str(user.id)
                elif hasattr(user, 'user_id'):
                    user_id = str(user.user_id)
            
            # Timestamp is handled by logging formatter, but requirement says:
            # "Logs action name, timestamp, user ID ... and success/failure status."
            # We can include them in the message.
            
            try:
                result = func(*args, **kwargs)
                # Log success
                msg = f"Action: {action_name} | UserID: {user_id} | Status: SUCCESS"
                system_logger.info(msg)
                return result
            except PermissionError as e:
                # Auth failure - log to security.log
                msg = f"Action: {action_name} | UserID: {user_id} | Status: FAILURE | Error: {str(e)}"
                security_logger.warning(msg)
                # Also log to system for continuity? Prompt says "Writes logs to: logs/system.log AND logs/security.log (for auth...)"
                # "AND" implies both maybe? Or specific targets.
                # "logs/security.log (for auth/permission failures)"
                # I'll enable writing to security log for auth failures.
                # Should I re-raise? "Must NOT interrupt program flow." -> This usually means the logging shouldn't, but the error?
                # "Must NOT interrupt program flow" usually refers to the logging mechanism itself not causing a crash.
                # If the function raises, the decorator should probably re-raise after logging, unless it's supposed to suppress.
                # Standard Python decorators usually re-raise.
                # If I suppress, the caller won't know permission failed.
                # But if I re-raise, checking "Must NOT interrupt program flow"...
                # Usually means "Logging shouldn't crash".
                # I will re-raise the PermissionError because that's critical business logic (Auth).
                raise e
            except Exception as e:
                # General failure
                msg = f"Action: {action_name} | UserID: {user_id} | Status: FAILURE | Error: {str(e)}"
                system_logger.error(msg)
                raise e
                
        return wrapper
    return decorator
