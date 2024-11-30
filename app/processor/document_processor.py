# app/processor/document_processor.py
from langchain_google_community import GoogleDriveLoader
from typing import List, Optional, Dict
from datetime import datetime
from langchain.docstore.document import Document
from google.oauth2.credentials import Credentials
import uuid
import os

from .chunk_processor import ChunkProcessor
from .context_generator import ContextGenerator
from ..database.vector_store import VectorStore
from ..database.metadata_store import MetadataStore
from ..models.metadata import DocumentMetadata
from ..config.settings import Settings

class DocumentProcessor:
    def __init__(
        self,
        vector_store: VectorStore,
        metadata_store: MetadataStore,
        context_generator: ContextGenerator,
        chunk_processor: ChunkProcessor,
        settings: Settings
    ):
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        self.context_generator = context_generator
        self.chunk_processor = chunk_processor
        self.settings = settings
        self.loader = None

    def _initialize_loader(self, credentials: Dict):
        """Initialize loader with OAuth credentials"""
        creds = Credentials.from_authorized_user_info(credentials)
        self.loader = GoogleDriveLoader(
            credentials=creds,
            file_ids=[],
            recursive=False
        )

    async def process_file(self, file_id: str, credentials: Dict) -> str:
        """Process a single file"""
        metadata = None
        try:
            self._initialize_loader(credentials)
            
            # Create metadata entry
            metadata = DocumentMetadata(
                document_id=str(uuid.uuid4()),
                original_file_name=file_id,
                drive_id=file_id,
                drive_path="",
                file_size=0,
                created_at=datetime.utcnow(),
                modified_at=datetime.utcnow(),
                status="processing"
            )
            
            doc_id = await self.metadata_store.create(metadata)

            # Load document
            self.loader.file_ids = [file_id]
            documents = self.loader.load()
            
            if not documents:
                raise Exception(f"No document found with ID: {file_id}")
            
            document = documents[0]

            # Update metadata with actual file name if available
            if hasattr(document, 'metadata'):
                await self.metadata_store.update_status(
                    doc_id=doc_id,
                    status="processing",
                    file_name=document.metadata.get('source', ''),
                    file_size=document.metadata.get('size', 0)
                )

            # Get full document content for context
            full_content = self.chunk_processor.get_document_text(document)

            # Split into chunks
            chunks = await self.chunk_processor.split_document(document)

            # Generate context and store chunks
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                try:
                    # Generate context
                    context = await self.context_generator.generate_context(
                        document_content=full_content,
                        chunk_content=chunk.page_content
                    )
                    
                    # Combine context with chunk
                    contextualized_chunk = Document(
                        page_content=f"{context}\n\n{chunk.page_content}",
                        metadata={
                            **chunk.metadata,
                            "document_id": doc_id,
                            "drive_id": file_id,
                            "context_generated": True,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "processed_at": datetime.utcnow().isoformat()
                        }
                    )
                    processed_chunks.append(contextualized_chunk)
                
                except Exception as chunk_error:
                    print(f"Error processing chunk {i}: {str(chunk_error)}")
                    continue

            if not processed_chunks:
                raise Exception("No chunks were successfully processed")

            # Store in vector database
            await self.vector_store.add_documents(processed_chunks)

            # Update metadata with success status
            await self.metadata_store.update_status(
                doc_id=doc_id,
                status="completed",
                chunk_count=len(processed_chunks)
            )

            return doc_id

        except Exception as e:
            # Update metadata with error status
            if metadata and metadata.document_id:
                await self.metadata_store.update_status(
                    doc_id=metadata.document_id,
                    status="failed",
                    error=str(e)
                )
            raise Exception(f"Document processing failed: {str(e)}")

    async def get_processing_status(self, doc_id: str) -> dict:
        """Get current processing status of a document"""
        return await self.metadata_store.get_document(doc_id)