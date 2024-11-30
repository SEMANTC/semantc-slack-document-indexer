# app/auth/token_storage.py

from google.cloud import firestore
from typing import Optional, Dict
import json

class TokenStorage:
    def __init__(self, project_id: str):
        self.db = firestore.Client(project_id)
        self.collection = self.db.collection('user_tokens')

    async def save_token(self, user_id: str, token_data: Dict) -> None:
        """Save token data for a user"""
        doc_ref = self.collection.document(user_id)
        doc_ref.set({
            'token_data': token_data,
            'updated_at': firestore.SERVER_TIMESTAMP
        })

    async def get_token(self, user_id: str) -> Optional[Dict]:
        """Get token data for a user"""
        doc_ref = self.collection.document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get('token_data')
        return None

    async def delete_token(self, user_id: str) -> None:
        """Delete token data for a user"""
        doc_ref = self.collection.document(user_id)
        doc_ref.delete()