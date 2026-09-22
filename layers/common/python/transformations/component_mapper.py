from errors.main.fhir_resource_error import FhirResourceError
from transformations.component_payload import map_component_to_payload
from fhir.fhir_value_accessor import get_accessor

def map_components_to_data(resource_components, request_components):
    """
    Maps each requested component to its FHIR resource data,
    building two arrays used for processing and updating
    Args:
        resource_components (list): list of components from the FHIR resource
        request_components (list[dict]): Components requested by the caller
    Returns:
        - list: FHIR components that will be updated after processing
        - list: Serialized payloads ({ signal, metadata, value_type })
                to be sent to the processing Lambda
    """
    arr_resource_components_to_change = []
    arr_data_from_resource_components = []

    for request_component in request_components:
        resource_component_to_change = get_component_to_change_by_index(
            resource_components,
            request_component["index"]
        )

        validate_change_field(
            resource_component_to_change,
            request_component["changeField"]
        )

        arr_resource_components_to_change.append(resource_component_to_change)
        arr_data_from_resource_components.append(
            map_component_to_payload(resource_component_to_change)
        )
    return (
        arr_resource_components_to_change,
        arr_data_from_resource_components
    )

def get_component_to_change_by_index(resource_components, index):
    """Finds a FHIR component by position in the resource"""
    try:
        index = int(index)
    except (TypeError, ValueError):
        raise FhirResourceError(f"Invalid component index: {index}")

    if index < 0 or index >= len(resource_components):
        raise FhirResourceError(f"Component index {index} is out of range")
    return resource_components[index]

def validate_change_field(resource_component, change_field):
    """Checks if the change_field request field exists and has a value in the FHIR component"""
    accessor = get_accessor(resource_component)
    value = accessor["get"](resource_component, change_field)

    if value is None:
        raise FhirResourceError(
            f"Change field '{change_field}' not found in component"
        )