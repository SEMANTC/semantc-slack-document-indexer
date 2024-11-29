# app/cloud_function/utils.py

from google.cloud import storage
from typing import Dict, Any
import json

def get_file_metadata(event: Dict[str, Any]) -> Dict[str, Any]:
    """EXTRACT AND VALIDATE FILE METADATA FROM EVENT"""
    try:
        return {
            "name": event.get("name"),
            "bucket": event.get("bucket"),
            "content_type": event.get("contentType"),
            "size": event.get("size"),
            "created": event.get("timeCreated"),
            "updated": event.get("updated")
        }
    except Exception as e:
        raise ValueError(f"invalid event data: {str(e)}")

def is_supported_file_type(content_type: str) -> bool:
    """CHECK IF FILE TYPE IS SUPPORTED"""
    supported_types = [
        'application/pdf',
        'text/plain',
        'application/vnd.google-apps.document',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    return content_type in supported_types

def should_process_file(event: Dict[str, Any]) -> bool:
    """DETERMINE IF FILE SHOULD BE PROCESSED"""
    metadata = get_file_metadata(event)
    return (
        metadata.get("content_type") and
        is_supported_file_type(metadata["content_type"])
    )