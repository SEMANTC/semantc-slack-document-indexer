# app/auth/google_auth.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from typing import Dict, Optional
import json

class GoogleDriveAuth:
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.flow = None

    def get_authorization_url(self) -> str:
        """Get URL for OAuth consent screen"""
        self.flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES
        )
        
        auth_url, _ = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return auth_url

    def get_credentials(self, code: str) -> Dict:
        """Exchange auth code for credentials"""
        self.flow.fetch_token(code=code)
        credentials = self.flow.credentials
        
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

    @staticmethod
    def credentials_from_dict(creds_dict: Dict) -> Credentials:
        """Create credentials object from dictionary"""
        return Credentials.from_authorized_user_info(creds_dict)

    @staticmethod
    def refresh_credentials(credentials: Credentials) -> Optional[Dict]:
        """Refresh credentials if expired"""
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            return {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
        return None