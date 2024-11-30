# app/models/drive.py

from pydantic import BaseModel
from typing import List, Optional

class DriveFile(BaseModel):
    id: str
    name: str
    mime_type: str
    web_view_link: Optional[str]

class DriveFolder(BaseModel):
    id: str
    name: str
    path: str