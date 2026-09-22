from fhir.fhir_value_accessor import get_accessor

# Maps each FHIR value type to a function that extracts its metadata
metadata_extractors = {
    "valueSampledData": lambda component: {
        "period": component["valueSampledData"].get("period")
    }
}

def map_component_to_payload(component):
    """
    Converts a FHIR component into a normalized payload
    to be sent to the processing Lambda
    Returns:
        dict: Normalized payload with keys:
            - signal (str|None): the raw signal data as a space-separated string
            - metadata (dict): extra fields from the component
            - value_type (str): the detected FHIR value type
    """
    accessor = get_accessor(component)
    value_type = accessor["value_type"]
    data_field = accessor["data_field"]

    signal = accessor["get"](component, data_field)
    metadata = metadata_extractors.get(value_type, lambda c: {})(component)

    return {
        "signal": str(signal) if signal is not None else None,
        "metadata": metadata,
        "value_type": value_type
    }