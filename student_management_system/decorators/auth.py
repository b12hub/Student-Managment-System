from functools import wraps

def require_role(required_role: str):
    """
    Decorator to check if the current user has the required role.
    Raises PermissionError if unauthorized.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if 'current_user' is in kwargs
            # The Requirement says: "Checks if `current_user` keyword argument exists."
            if 'current_user' not in kwargs:
                # If current_user is missing, it's a usage error or unauthorized context.
                # Strictly following: "If not authorized, raises PermissionError."
                # Missing user implies not authorized.
                raise PermissionError("Authorization failed: No user provided.")
            
            user = kwargs['current_user']
            # Assuming user object has a 'role' attribute as per requirements
            if not hasattr(user, 'role') or user.role != required_role:
                raise PermissionError(f"Authorization failed: User does not have role '{required_role}'.")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
