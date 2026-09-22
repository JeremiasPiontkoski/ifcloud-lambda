from errors.main.app_error import AppError


class ProcessingError(AppError):
    """
    Exception raised when a processing Lambda returns an error response (success=False)
    Holds the full structured body returned by the script runner
        and passes it through to the API response.
    """
    def __init__(self, body: dict):
        super().__init__(message=body.get("message", "Script execution error"))
        self.body = body

    def to_json(self):
        """
        Returns the original body from the script runner.
        """
        return self.body