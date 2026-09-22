from errors.main.app_error import AppError

class FhirResourceError(AppError):
    """Exception raised for errors related to FHIR resource processing"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)