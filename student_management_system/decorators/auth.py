from functools import wraps

def require_role(required_role: str):
    """
    Decorator to check if the current user has the required role.
    Raises PermissionError if unauthorized.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'current_user' not in kwargs:
                raise PermissionError("Authorization failed: No user provided.")
            
            user = kwargs['current_user']
            if not hasattr(user, '_role') or user._role != required_role:
                raise PermissionError(f"Authorization failed: User does not have role '{required_role}'.")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
