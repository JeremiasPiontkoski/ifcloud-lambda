from errors.main.fhir_resource_error import FhirResourceError

# Maps each request type to a function that builds the FHIR URL path
_request_strategies = {
    "byId": lambda params:
        f"{params['resourceType']}/{params['id']}",
    "byIdAndMinute": lambda params:
        f"{params['resourceType']}/{params['id']}/data/{params['minute']}",
    "byIdAndMinuteInterval": lambda params:
        f"{params['resourceType']}/{params['id']}/data/{params['initialMinute']}/{params['finalMinute']}",
}

def build_fhir_url(type_request, params):
    """
    Builds a FHIR API URL path based on the request type
    Args:
        type_request (str): The request strategy to use
        params (dict): URL parameters. Required keys vary by type_request:
            - byId: resourceType, id
            - byIdAndMinute: resourceType, id, minute
            - byIdAndMinuteInterval: resourceType, id, initialMinute, finalMinute
    Returns:
        str: The built URL path.
            Examples:
                "Observation/123"
                "Observation/123/data/0"
                "Observation/123/data/0/5"
    Raises:
        FhirResourceError: If type_request is not a supported strategy
    """
    strategy = _request_strategies.get(type_request)
    if not strategy:
        raise FhirResourceError(f"Unknown request type: '{type_request}'")
    return strategy(params)