import time
import requests
from errors.main.fhir_resource_error import FhirResourceError

class FhirApi:
    """
    Client for the FHIR API
    Handles authentication using client credentials (OAuth2),
    automatic token refresh, and HTTP requests to FHIR resources
    Usage:
        resource = fhir_api.get("/Observation/123/data/0")
    """

    # Refresh the token this many seconds before it actually expires
    TOKEN_EXPIRATION_BUFFER = 30

    def __init__(self):
        self.base_url = "https://if4health.charqueadas.ifsul.edu.br/biofass/"
        self.grant_type = "client_credentials"
        self.client_id = "0a67c45b-b57-ifcloud-jeremias"
        self.client_secret = "ae5cd7d7ceb433033ade7d456077d7b8ea8be2d4557e8c832702900dda2c3df5"

        self.token = None
        self.token_expires_at = 0
        self.session = requests.Session()

    def _authenticate(self):
        """
        Requests a new access token from the FHIR API auth endpoint
        and updates the session headers with the new token
        """
        url = f"{self.base_url}/auth/token"
        payload = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        self.token = data["access_token"]
        self.token_expires_at = time.time() + data["expires_in"]
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}"
        })

    def _token_expired(self):
        """Checks if the current token is missing or expired"""
        return (
            self.token is None
            or time.time() >= (self.token_expires_at - self.TOKEN_EXPIRATION_BUFFER)
        )

    def _ensure_authenticated(self):
        """Authenticates if the current token is expired or missing"""
        if self._token_expired():
            self._authenticate()

    def get(self, resource):
        """Fetches a FHIR resource by its path"""
        try:
            self._ensure_authenticated()

            url = f"{self.base_url}/{resource.lstrip('/')}"
            response = self.session.get(url, timeout=30)

            if response.status_code == 401:
                self.token = None
                self._authenticate()
                response = self.session.get(url, timeout=30)

            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            raise FhirResourceError(str(e))
        except requests.RequestException as e:
            raise FhirResourceError(f"Failed to connect to FHIR API: {str(e)}")

fhir_api = FhirApi()