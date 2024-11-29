# app/models/metadata.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DocumentMetadata:
    """METADATA FOR A PROCESSED DOCUMENT"""
    document_id: str
    original_file_name: str
    drive_id: str
    drive_path: str
    file_size: int
    created_at: datetime
    modified_at: datetime
    status: str = "pending"
    chunk_count: int = 0
    error: Optional[str] = None