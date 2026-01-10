import logging
import os
import functools
from datetime import datetime

def _setup_logger(name, log_file, level=logging.INFO):
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    handler = logging.FileHandler(log_file)        
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

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
                if hasattr(user, '_user_id'):
                    user_id = str(user._user_id)
            
            try:
                result = func(*args, **kwargs)
                msg = f"Action: {action_name} | UserID: {user_id} | Status: SUCCESS"
                system_logger.info(msg)
                return result
            except PermissionError as e:
                msg = f"Action: {action_name} | UserID: {user_id} | Status: FAILURE | Error: {str(e)}"
                security_logger.warning(msg)
                raise e
            except Exception as e:
                msg = f"Action: {action_name} | UserID: {user_id} | Status: FAILURE | Error: {str(e)}"
                system_logger.error(msg)
                raise e
                
        return wrapper
    return decorator
