# app/utils/helpers.py

import uuid
from datetime import datetime
from typing import Any, Dict

def generate_id(prefix: str = "") -> str:
    """GENERATE A UNIQUE ID"""
    return f"{prefix}{str(uuid.uuid4())}"

def format_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """FORMAT METADATA FOR STORAGE"""
    return {
        **metadata,
        "created_at": metadata.get("created_at", datetime.utcnow()),
        "updated_at": datetime.utcnow()
    }