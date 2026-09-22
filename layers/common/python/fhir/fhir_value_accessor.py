from errors.main.fhir_resource_error import FhirResourceError

# Maps each supported FHIR value type to its read/write strategy
value_accessors = {
    "valueSampledData": {
        "data_field": "data",
        "get": lambda component, field:
            component["valueSampledData"].get(field),
        "set": lambda component, field, value:
            component["valueSampledData"].update({field: value})
    }
}

def detect_value_type(component):
    """Detects which FHIR value type is present in a component"""
    for key in value_accessors:
        if key in component:
            return key

    raise FhirResourceError(
        f"Unsupported FHIR value type. Keys found: {', '.join(component.keys())}"
    )


def get_accessor(component):
    """
    Returns the read/write accessor for a given FHIR component
    Returns:
        dict: The accessor for the detected value type, with keys:
            - data_field (str): the main data field name
            - get (callable): reads a field value from the component
            - set (callable): writes a value to a field in the component
            - value_type (str): the detected FHIR value type key
    Raises:
        FhirResourceError: If no supported value type is found in the component
    """
    value_type = detect_value_type(component)
    return {
        **value_accessors[value_type], 
        "value_type": value_type
    }