# app/models/auth.py

from pydantic import BaseModel
from typing import Optional, List

class TokenData(BaseModel):
    token: str
    refresh_token: Optional[str]
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]

class UserAuth(BaseModel):
    user_id: str
    token_data: TokenData