from errors.processing.app_error import AppError

class ProcessingError(AppError):
    """Exception raised for general data processing failures"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)