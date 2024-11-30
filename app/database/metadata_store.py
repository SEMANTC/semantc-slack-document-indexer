# app/database/metadata_store.py

from google.cloud import firestore
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.metadata import DocumentMetadata

class MetadataStore:
    """HANDLES DOCUMENT METADATA STORAGE IN FIRESTORE"""
    
    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)
        self.collection = self.db.collection('document_metadata')
    
    async def create(self, metadata: DocumentMetadata) -> str:
        """CREATES A NEW DOCUMENT METADATA ENTRY"""
        doc_ref = self.collection.document(metadata.document_id)
        doc_ref.set({
            'original_file': {
                'name': metadata.original_file_name,
                'drive_id': metadata.drive_id,
                'path': metadata.drive_path,
                'size': metadata.file_size,
                'created_at': metadata.created_at,
                'modified_at': metadata.modified_at
            },
            'processing': {
                'status': metadata.status,
                'chunk_count': metadata.chunk_count,
                'last_processed': firestore.SERVER_TIMESTAMP,
                'error': metadata.error
            }
        })
        return metadata.document_id
    
    async def update_status(self, doc_id: str, status: str, 
                          chunk_count: Optional[int] = None,
                          error: Optional[str] = None,
                          file_name: Optional[str] = None,
                          file_size: Optional[int] = None) -> None:
        """UPDATES DOCUMENT METADATA"""
        doc_ref = self.collection.document(doc_id)
        update_data = {
            'processing.status': status,
            'processing.last_processed': firestore.SERVER_TIMESTAMP
        }
        
        if chunk_count is not None:
            update_data['processing.chunk_count'] = chunk_count
        if error is not None:
            update_data['processing.error'] = error
        if file_name is not None:
            update_data['original_file.name'] = file_name
        if file_size is not None:
            update_data['original_file.size'] = file_size
        
        doc_ref.update(update_data)
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """RETRIEVES DOCUMENT METADATA BY ID"""
        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None