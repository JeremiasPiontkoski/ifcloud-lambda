from errors.main.validation_error import ValidationError

def _validate_base(data):
    """
    Validates the fields present in all request types
    Args:
        data (dict): The request body
    Returns:
        list[str]: List of error messages. Empty if all fields are valid.
    """
    errors: list[str] = []

    # recourceType
    if "resourceType" not in data or data["resourceType"] is None:
        errors.append("resourceType is required!")
    elif not isinstance(data["resourceType"], str):
        errors.append("resourceType must be a string!")

    # id
    if "id" not in data or data["id"] is None:
        errors.append("id is required!")
    elif not isinstance(data["id"], str):
        errors.append("id must be a string!")

    # scriptName
    if "scriptName" not in data or data["scriptName"] is None:
        errors.append("scriptName is required!")
    elif not isinstance(data["scriptName"], str):
        errors.append("scriptName must be a string!")

    # returnOnlyFieldsComponents
    if "returnOnlyFieldsComponents" not in data or data["returnOnlyFieldsComponents"] is None:
        errors.append("returnOnlyFieldsComponents is required!")
    elif not isinstance(data["returnOnlyFieldsComponents"], bool):
        errors.append("returnOnlyFieldsComponents must be a boolean value!")

    # typeRequest
    valid_types = {"byId", "byIdAndMinute", "byIdAndMinuteInterval"}
    if "typeRequest" not in data or data["typeRequest"] is None:
        errors.append("typeRequest is required!")
    elif not isinstance(data["typeRequest"], str):
        errors.append("typeRequest must be a string!")
    elif data["typeRequest"] not in valid_types:
        errors.append("typeRequest must be one of: byId, byIdAndMinute, byIdAndMinuteInterval!")

    # components
    components = data.get("components")
    if components is None:
        errors.append("components is required!")
    elif not isinstance(components, list):
        errors.append("components must be an array!")
    elif len(components) == 0:
        errors.append("components must contain at least one item!")
    else:
        for item in components:
            if not isinstance(item, dict):
                errors.append("Each component must be an object!")
                continue
            
            if "index" not in item or item["index"] is None:
                errors.append("index is required!")
                
            elif not isinstance(item["index"], (int, str)):
                errors.append("index must be a number!")
                
            if "changeField" not in item or item["changeField"] is None:
                errors.append("changeField is required!")
                
            elif not isinstance(item["changeField"], str):
                errors.append("changeField must be a string!")
    return errors

def _validate_by_id(data):
    """Validates fields specific to the "byId" request type"""
    return []

def _validate_by_id_and_minute(data: dict) -> list[str]:
    """Validates fields specific to the "byIdAndMinute" request type"""
    errors: list[str] = []
    minute = data.get("minute")

    if minute is None:
        errors.append("minute is required for byIdAndMinute!")
    elif not isinstance(minute, int):
        errors.append("minute must be a number!")
    elif minute < 0:
        errors.append("minute must be equals or greater than 0!")
    return errors

def _validate_by_id_and_minute_interval(data: dict) -> list[str]:
    """Validates fields specific to the "byIdAndMinuteInterval" request type"""
    errors: list[str] = []
    initial = data.get("initialMinute")
    final = data.get("finalMinute")

    if initial is None:
        errors.append("initialMinute is required for byIdAndMinuteInterval!")
    elif not isinstance(initial, int):
        errors.append("initialMinute must be a number!")
    elif initial < 0:
        errors.append("initialMinute must be equals or greater than 0!")

    if final is None:
        errors.append("finalMinute is required for byIdAndMinuteInterval!")
    elif not isinstance(final, int):
        errors.append("finalMinute must be a number!")
    elif final < 1:
        errors.append("finalMinute must be greater than 0!")

    if (
        errors == []
        and isinstance(initial, int)
        and isinstance(final, int)
        and final <= initial
    ):
        errors.append("finalMinute must be greater than initialMinute!")
    return errors


# Maps each request type to its specific validator
_TYPE_VALIDATORS = {
    "byId": _validate_by_id,
    "byIdAndMinute": _validate_by_id_and_minute,
    "byIdAndMinuteInterval": _validate_by_id_and_minute_interval,
}

def validate_operation_starter(data):
    """
    Validates the full request body
    Runs in two steps:
        1. Validates all common fields (resourceType, id, scriptName, etc)
        2. Validates fields specific to the given typeRequest
    """
    errors: list[str] = []
    errors.extend(_validate_base(data))

    type_validator = _TYPE_VALIDATORS.get(data.get("typeRequest"))
    if type_validator:
        errors.extend(type_validator(data))
    if errors:
        raise ValidationError(errors)