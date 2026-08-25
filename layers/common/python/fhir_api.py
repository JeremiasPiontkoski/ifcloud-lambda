import os
import time
import requests


class FhirApi:

    TOKEN_EXPIRATION_BUFFER = 30

    def __init__(self):
        self.base_url = "URL"
        self.grant_type = "client_credentials"
        self.client_id = "CLIENT_ID"
        self.client_secret = "SECRET"

        self.token = None
        self.token_expires_at = 0

        self.session = requests.Session()

    def _authenticate(self):
        url = f"{self.base_url}/auth/token"

        payload = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(
            url,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        self.token = data["access_token"]

        expires_in = data["expires_in"]

        self.token_expires_at = (
            time.time() + expires_in
        )

        self.session.headers.update({
            "Authorization": f"Bearer {self.token}"
        })

    def _token_expired(self):
        return (
            self.token is None
            or time.time() >= (
                self.token_expires_at
                - self.TOKEN_EXPIRATION_BUFFER
            )
        )

    def _ensure_authenticated(self):
        if self._token_expired():
            self._authenticate()

    def get(self, resource):
        self._ensure_authenticated()

        url = f"{self.base_url}/{resource.lstrip('/')}"

        response = self.session.get(
            url,
            timeout=30
        )

        # Token rejeitado pela API.
        if response.status_code == 401:

            self.token = None

            self._authenticate()

            response = self.session.get(
                url,
                timeout=30
            )

        response.raise_for_status()

        return response.json()

    def teste(self):
        print(self.base_url)


fhir_api = FhirApi()