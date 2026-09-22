from fhir.fhir_value_accessor import get_accessor

def apply_processed_values(components_to_change, request_components, processed_data):
    """
    Writes the processed values back into the original FHIR components
    Each processed value is normalized to a plain string before being written
    Args:
        components_to_change (list): Original FHIR components to be updated
        request_components (list[dict]): Components field in the request sended
        processed_data (list): Output values returned by the processing Lambda
    Returns:
        list: The updated FHIR components with processed values applied
    Example:
        Input processed_data:  [[72.3, 74.1, 71.8]]
        Written to component:  "72.3 74.1 71.8"
    """
    for i, raw_value in enumerate(processed_data):
        field = request_components[i]["changeField"]

        if isinstance(raw_value, list):
            normalized_value = " ".join(map(str, raw_value))
        elif raw_value is not None:
            normalized_value = (
                str(raw_value)
                .replace("\r\n", "")
                .replace("\n", "")
                .replace("\r", "")
            )
        else:
            normalized_value = None

        accessor = get_accessor(components_to_change[i])
        accessor["set"](components_to_change[i], field, normalized_value)
    return components_to_change