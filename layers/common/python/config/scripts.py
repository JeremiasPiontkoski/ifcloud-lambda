import os

def _load_supported_scripts():
    """
    Reads the SUPPORTED_SCRIPTS environment variable and parses it
    into a dictionary mapping script names to Lambda function names.
    Example: "calcBPM.py:CalcBPMLambda,HelloWorld.py:HelloWorld"
    Returns:
        dict: { "calcBPM.py": "CalcBPMLambda", ... }
              Returns an empty dict if the variable is not set or is empty.
    """
    raw = os.environ.get("SUPPORTED_SCRIPTS", "")
    if not raw:
        return {}
    
    scripts = {}
    for entry in raw.split(","):
        try:
            script_name, function_name = entry.strip().split(":")
            scripts[script_name.strip()] = function_name.strip()
        except ValueError:
            continue
    return scripts

SUPPORTED_SCRIPTS = _load_supported_scripts()