# exceptions.py (or in your service file)
class APIError(Exception):
    """Base exception for system"""

    pass


class DuplicateError(APIError):
    """Raised when trying to create/update to a duplicate option"""

    pass


class NotFoundError(APIError):
    """Raised when option doesn't exist"""

    pass
