# Default imports
import requests
import json

# Django imports
from django.template import Context, Template

# Project Model imports
from superbill.models import (
    EDIPayer,
    EDIPayerEndpoint,
    EDIClaim
)

# Utility imports
from superbill.edi_engine import Dynamic837ClaimEngine

class EDIRequestDispatcher:
    """
    Dynamically dispatch requests to payer endpoints
    with automatic payload, headers, and URL construction.
    """

    def __init__(self, payer_id, endpoint_type):
        self.payer = EDIPayer.objects.get(id=payer_id)
        self.endpoint_type = endpoint_type
        self.endpoint = self.get_endpoint()
        self.payload_profile = self.get_payload_profile()

    # Get the correct endpoint
    def get_endpoint(self):
        endpoint = EDIPayerEndpoint.objects.filter(
            payer=self.payer,
            endpoint_type=self.endpoint_type
        ).first()
        if not endpoint:
            raise ValueError(f"No endpoint configured for {self.payer.name} and type {self.endpoint_type}")
        return endpoint

    # Get active payload profile
    def get_payload_profile(self):
        return self.endpoint.payload_profiles.filter(is_active=True).order_by("-updated_at").first()

    # Build headers dynamically
    def build_headers(self, extra_headers=None):
        headers = {"Content-Type": "application/json"}
        creds = self.payer.credentials or {}
        auth_type = creds.get("auth_type", "").lower()

        if auth_type == "bearer" and creds.get("api_key"):
            headers["Authorization"] = f"Bearer {creds['api_key']}"

        elif auth_type == "basic" and creds.get("username") and creds.get("password"):
            import base64
            token = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"

        if creds.get("headers"):
            headers.update(creds["headers"])

        if extra_headers:
            headers.update(extra_headers)

        return headers

    # Build payload
    def build_payload(self, claim_id=None):
        if not self.payload_profile:
            return None

        # JSON / FHIR
        if self.payload_profile.profile_type in ["JSON", "FHIR"]:
            claim = EDIClaim.objects.prefetch_related("service_lines", "diagnoses").get(id=claim_id)
            claim_dict = self.model_to_dict(claim)
            template_str = json.dumps(self.payload_profile.payload_template)
            rendered = Template(template_str).render({"claim": claim_dict})
            return json.loads(rendered)
        
        elif self.payload_profile.profile_type == "EDI837":
            claim = EDIClaim.objects.prefetch_related("service_lines", "diagnoses").get(id=claim_id)
            engine = Dynamic837ClaimEngine()
            # Generate EDI837 payload as plain text
            edi_lines = list(engine.generate(claim, self.payer))
            return "".join(edi_lines)
    
    # Send request
    def send_request(self, http_method="POST", claim_id=None, extra_headers=None):
        url = f"{self.payer.base_url.rstrip('/')}/{self.endpoint.path.lstrip('/')}"
        headers = self.build_headers(extra_headers)
        payload = self.build_payload(claim_id)
        params = self.endpoint.query_params or {}

        method = http_method.upper()
        if method == "POST":
            response = requests.post(url, json=payload, headers=headers, params=params)
        elif method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "PUT":
            response = requests.put(url, json=payload, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        return response.json()
