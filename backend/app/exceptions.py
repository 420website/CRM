# exceptions.py (or in your service file)
class APIError(Exception):
    """Base exception for system"""

    status_code = 500

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class DuplicateError(APIError):
    status_code = 409


class NotFoundError(APIError):
    status_code = 404


class UnauthorizedError(APIError):
    """Identity is unauthenticated."""

    status_code = 401


class ForbiddenError(APIError):
    """Indentity is known but doesn't have access."""

    status_code = 403


class SessionLockedError(APIError):
    status_code = 423


class SessionExpiredError(APIError):
    status_code = 410
    message = "Session has expired."


# Analytics related
class ContextRetrievalError(APIError):
    """Bad query for the error"""

    pass


class AnthropicRequestError(APIError):
    """Bad query for the error"""

    pass
