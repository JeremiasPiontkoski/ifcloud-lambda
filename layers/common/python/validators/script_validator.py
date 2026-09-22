from config.scripts import SUPPORTED_SCRIPTS
from errors.main.validation_error import ValidationError

def validate_script(script_name):
    """Checks if a script name is registered as a supported Lambda function"""
    if script_name not in SUPPORTED_SCRIPTS:
        raise ValidationError(
            [f"Python script '{script_name}' not found"]
        )