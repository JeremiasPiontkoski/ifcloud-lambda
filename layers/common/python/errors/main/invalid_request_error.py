from errors.main.app_error import AppError

class InvalidRequestError(AppError):
    """Exception raised when an incoming request body is malformed or invalid"""
    def __init__(self, message: str = "Invalid JSON body"):
        super().__init__(message, status_code=400)