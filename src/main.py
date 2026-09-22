import json
import os
import boto3
from config.scripts import SUPPORTED_SCRIPTS
from errors.main.fhir_resource_error import FhirResourceError
from errors.main.app_error import AppError
from errors.main.processing_error import ProcessingError
from errors.main.invalid_request_error import InvalidRequestError
from fhir_api import fhir_api
from transformations.component_mapper import map_components_to_data
from transformations.component_uploader import apply_processed_values
from validators.operation_starter_validator import validate_operation_starter
from validators.script_validator import validate_script
from fhir.fhir_url_builder import build_fhir_url

# Development
lambda_client = boto3.client(
    "lambda",
    region_name="us-east-1",
    endpoint_url=os.environ.get("LAMBDA_ENDPOINT"),
    aws_access_key_id="dummy",
    aws_secret_access_key="dummy",
)

# Production
# lambda_client = boto3.client(
#     "lambda",
#     region_name="sa-east-1"
# )

def _parse_body(event):
    """
    Extracts and parses the request body from the Lambda event
    Handles three cases:
        - API Gateway: event["body"] is a JSON string → parsed to dict
        - Direct invocation (console, tests): event has no "body" → used as-is
        - event["body"] is already a dict → returned as-is
    """
    try:
        if "body" not in event:
            return event

        raw = event["body"]
        if isinstance(raw, dict):
            return raw

        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        raise InvalidRequestError("Invalid JSON body")

def _invoke_script(script_name, data):
    """
    Invokes a processing Lambda function and returns its result
    Sends the data as a payload and reads the response.
    If the Lambda crashes (unhandled exception), AWS returns an errorType
    field instead of a body — this is detected and raised as ProcessingError.
    Args:
        script_name (str): The script name. Used to resolve the Lambda function name
        data (list):       List of component payloads to process
    Raises:
        ProcessingError: If the Lambda crashed or returned success=False
    """
    response = lambda_client.invoke(
        FunctionName=SUPPORTED_SCRIPTS[script_name],
        InvocationType="RequestResponse",
        Payload=json.dumps({"data": data}),
    )
    payload = json.loads(response["Payload"].read())

    # AWS wraps unhandled Lambda exceptions in errorType instead of body
    if "errorType" in payload:
        raise ProcessingError({
            "status": "error",
            "error": "ProcessingError",
            "message": f"Script execution failed: {payload.get('errorMessage')}"
        })

    if not payload.get("success"):
        raise ProcessingError(json.loads(payload["body"]))
    return json.loads(payload["body"])

def _build_response(resource, updated_components, return_only_fields_components):
    """
    Builds the final API response with the updated FHIR resource
    Args:
        resource (dict): The original FHIR resource
        updated_components (list): Components with processed values applied
        return_only_fields_components (bool): If True, returns only the updated
                                              components instead of the full resource
    """
    if return_only_fields_components:
        data = updated_components
    else:
        data = {
            **resource,
            "component": updated_components
        }
    return {
        "statusCode": 200,
        "body": json.dumps(data)
    }

def lambda_handler(event, context):
    """
    Main entry point for the operation starter Lambda.
    Orchestrates the full processing pipeline:
        1. Parses and validates the request body
        2. Builds the FHIR resource URL based on the request type
        3. Fetches the FHIR resource
        4. Maps the requested components to processing payloads
        5. Invokes the processing Lambda (script)
        6. Applies the processed values back to the FHIR components
        7. Returns the updated resource or components
    """
    try:
        body = _parse_body(event)
        validate_operation_starter(body)

        id = body["id"]
        minute = body.get("minute")
        initial_minute = body.get("initialMinute")
        final_minute = body.get("finalMinute")
        type_request = body["typeRequest"]
        components = body["components"]
        resource_type = body["resourceType"]
        script_name = body["scriptName"]
        return_only_fields_components = body["returnOnlyFieldsComponents"]

        validate_script(script_name)

        fhir_path = build_fhir_url(type_request, {
            "resourceType": resource_type,
            "id": id,
            "minute": minute,
            "initialMinute": initial_minute,
            "finalMinute": final_minute,
        })
        resource = fhir_api.get(fhir_path)
        fhir_components = resource.get("component")

        if not fhir_components:
            raise FhirResourceError("Resource does not contain components")

        (components_to_change, data_from_components) = map_components_to_data(
            fhir_components,
            components
        )
        processed_data = _invoke_script(
            script_name,
            data_from_components
        )
        updated_components = apply_processed_values(
            components_to_change,
            components,
            processed_data
        )
        return _build_response(
            resource,
            updated_components,
            return_only_fields_components
        )
    except AppError as e:
        return {
            "statusCode": e.status_code,
            "body": json.dumps(e.to_json())
        }
    except Exception as e:
        print("Erro:", str(e))
        print(f"TIPO: {type(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "error": "InternalServerError",
                "message": str(e)
            })
        }