import json
from fhir_api import fhir_api

def lambda_handler(event, context):
    try:
        
        observation_id = event["id"]
        minute = event["minute"]

        data = fhir_api.get(
            f"/Observation/{observation_id}/data/{minute}"
        )

        return {
            "statusCode": 200,
            "body": json.dumps(data)
        }

    except Exception as e:
        print("Erro:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }