class AppError(Exception):
    """Base exception class for application errors"""
    def __init__(self, message: str, status_code: int = 400, status: str = "error"):
        super().__init__(message)
        self.name = self.__class__.__name__
        self.status_code = status_code
        self.status = status

    def to_json(self):
        """Converts the exception details into a JSON-serializable dictionary"""
        return {
            "status": self.status,
            "error": self.name,
            "message": str(self)
        }