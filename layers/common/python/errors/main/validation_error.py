from errors.main.app_error import AppError


class ValidationError(AppError):
    """
    Raised when the request body fails validation.
    Example:
        raise ValidationError(["id is required!", "scriptName is required!"])
    Output (to_json):
        {
            "status": "error",
            "error": "ValidationError",
            "messages": ["id is required!", "scriptName is required!"]
        }
    """
    def __init__(self, messages: list[str]):
        super().__init__(message=", ".join(messages), status_code=400)
        self.messages = messages

    def to_json(self):
        """
        Returns error messages as an array
        """
        return {
            "status": self.status,
            "error": self.name,
            "messages": self.messages
        }