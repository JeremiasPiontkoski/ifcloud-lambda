class AppError(Exception):
    """Base exception class for all errors inside processing Lambdas (script runners)"""
    def __init__(self, message: str, status_code: int = 400, status: str = "error"):
        super().__init__(message)
        self.name = self.__class__.__name__
        self.status_code = status_code
        self.status = status

    def to_json(self):
        """
        Returns a dict representation of the error for the script runner response
        """
        return {
            "status": self.status,
            "error": self.name,
            "message": str(self)
        }