import time
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from app.core.config import settings

class UpworkAuthService:
    def __init__(self):
        self.client_id = settings.UPWORK_CLIENT_ID
        self.client_secret = settings.UPWORK_CLIENT_SECRET
        self.redirect_uri = settings.UPWORK_REDIRECT_URI
        self.token_path = settings.BASE_DIR / "tokens.json"
        self.token_url = "https://www.upwork.com/api/v3/oauth2/token"
        self.auth_url = "https://www.upwork.com/ab/developer-console/oauth2/authorize"

    def get_authorization_url(self) -> str:
        """Generates the URL for the initial user consent."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }
        prep = requests.Request('GET', self.auth_url, params=params).prepare()
        return prep.url

    def exchange_code_for_token(self, auth_code: str) -> Dict[str, Any]:
        """Exchanges the temporary auth code for access/refresh tokens."""
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }
        return self._update_token_state(data)

    def refresh_access_token(self) -> Dict[str, Any]:
        """Uses the refresh token to obtain a new access token."""
        tokens = self._load_from_disk()
        if not tokens or "refresh_token" not in tokens:
            raise ValueError("No refresh token available. Manual re-auth required.")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        return self._update_token_state(data)

    def get_valid_token(self) -> str:
        """
        The main entry point for other modules. 
        Returns a valid access token, refreshing it if necessary.
        """
        tokens = self._load_from_disk()
        if not tokens:
            raise ConnectionError("Service not authenticated. Run setup_auth first.")

        # Check if expired (with a 5-minute buffer)
        if time.time() > (tokens.get("expires_at", 0) - 300):
            print("Token expired or nearing expiry. Refreshing...")
            tokens = self.refresh_access_token()

        return tokens["access_token"]

    def _update_token_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper to hit the token endpoint and save result."""
        response = requests.post(self.token_url, data=data)
        if response.status_code != 200:
            raise Exception(f"OAuth Error: {response.status_code} - {response.text}")
        
        tokens = response.json()
        tokens["expires_at"] = time.time() + tokens["expires_in"]
        
        with open(self.token_path, "w") as f:
            json.dump(tokens, f)
        return tokens

    def _load_from_disk(self) -> Optional[Dict[str, Any]]:
        if not self.token_path.exists():
            return None
        with open(self.token_path, "r") as f:
            return json.load(f)

# Instantiate as a singleton for the app
auth_service = UpworkAuthService()