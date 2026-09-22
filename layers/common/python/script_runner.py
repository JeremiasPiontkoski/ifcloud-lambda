import numpy as np
import json
from errors.processing.app_error import AppError
from errors.processing.processing_error import ProcessingError

def _validate_derivations(received_derivations, min_derivations, max_derivations=None):
    """
    Validates the number of received derivations
    Args:
        received_derivations (int): Number of derivations received
        min_derivations (int):      Minimum number required (inclusive)
        max_derivations (int|None): Maximum number allowed (inclusive)
                                    None means no upper limit
    """
    if received_derivations < min_derivations:
        raise ProcessingError(
            f"This script requires minimal {min_derivations} derivation(s). "
            f"Received: {received_derivations}"
        )

    if (
        max_derivations is not None
        and max_derivations >= min_derivations
        and received_derivations > max_derivations
    ):
        raise ProcessingError(
            f"This script allows {max_derivations} derivation(s). "
            f"Received: {received_derivations}"
        )

    if received_derivations % min_derivations != 0:
        raise ProcessingError(
            f"This script requires a multiple of {min_derivations} derivation(s). "
            f"Received: {received_derivations}"
        )

def _prepare_signals(payloads):
    """
    Converts each payload's signal string into a numpy float array
    Returns:
        list[dict]: Same structure, with signal as np.ndarray of floats
    """
    try:
        return [
            {
                "signal": np.array([float(v) for v in p["signal"].split()]),
                "metadata": p.get("metadata", {})
            }
            for p in payloads
        ]
    except Exception:
        raise ProcessingError("Error to convert data to numpy arrays")

def run(process_function, payloads, prepare_signals=False, min_derivations=1, max_derivations=None):
    """
    Validates, prepares and runs a processing function over the given payloads
    This is the entry point for all processing Lambda scripts
    It handles validation, signal conversion, execution, and error formatting
    Args:
        process_function (callable): The algorithm to run
        payloads (list):             Raw payloads from the main Lambda
        prepare_signals (bool):      If True, converts signal strings to np.ndarray
        min_derivations (int):       Minimum number of payloads required
        max_derivations (int|None):  Maximum number of payloads allowed
                                     None means no upper limit
    Example success response:
        {
            "statusCode": 200,
            "success": True,
            "body": "[[72.3, 74.1, 71.8]]"
        }
    Example error response:
        {
            "statusCode": 400,
            "success": False,
            "body": "{\"status\": \"error\", \"error\": \"ProcessingError\", \"message\": \"...\"}"
        }
    """
    try:
        _validate_derivations(len(payloads), min_derivations, max_derivations)

        if prepare_signals:
            payloads = _prepare_signals(payloads)

        results = process_function(payloads)
        if not isinstance(results, list):
            results = [results]

        return {
            "statusCode": 200,
            "success": True,
            "body": json.dumps(results)
        }
    except AppError as e:
        return {
            "statusCode": e.status_code,
            "success": False,
            "body": json.dumps(e.to_json())
        }
    except Exception as e:
        print("Unexpected error:", str(e))
        return {
            "statusCode": 500,
            "success": False,
            "body": json.dumps({
                "status": "error",
                "error": "InternalServerError",
                "message": str(e)
            })
        }