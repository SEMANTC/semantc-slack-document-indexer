# app/processor/document_processor.py

from langchain.document_loaders import GoogleDriveLoader
from langchain.docstore.document import Document
from typing import List, Optional
from datetime import datetime
import uuid
import os
from .chunk_processor import ChunkProcessor
from .context_generator import ContextGenerator
from ..database.vector_store import VectorStore
from ..database.metadata_store import MetadataStore
from ..models.metadata import DocumentMetadata

class DocumentProcessor:
    def __init__(
        self,
        vector_store: VectorStore,
        metadata_store: MetadataStore,
        context_generator: ContextGenerator,
        chunk_processor: ChunkProcessor
    ):
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        self.context_generator = context_generator
        self.chunk_processor = chunk_processor
        self.loader = GoogleDriveLoader()

    async def process_file(self, file_id: str, file_path: str) -> str:
        """PROCESS A SINGLE FILE"""
        metadata = None
        try:
            # create metadata entry
            metadata = DocumentMetadata(
                document_id=str(uuid.uuid4()),
                original_file_name=os.path.basename(file_path),
                drive_id=file_id,
                drive_path=file_path,
                file_size=0,  # will be updated when file is loaded
                created_at=datetime.utcnow(),
                modified_at=datetime.utcnow(),
                status="processing"
            )
            
            doc_id = await self.metadata_store.create(metadata)

            # load document
            document = self.loader.load(file_path)

            # update file size in metadata if available
            if hasattr(document, 'metadata') and 'file_size' in document.metadata:
                await self.metadata_store.update_status(
                    doc_id=doc_id,
                    status="processing",
                    file_size=document.metadata['file_size']
                )

            # get full document content for context
            full_content = self.chunk_processor.get_document_text(document)

            # split into chunks
            chunks = await self.chunk_processor.split_document(document)

            # generate context and store chunks
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                try:
                    # generate context
                    context = await self.context_generator.generate_context(
                        document_content=full_content,
                        chunk_content=chunk.page_content
                    )
                    
                    # combine context with chunk
                    contextualized_chunk = Document(
                        page_content=f"{context}\n\n{chunk.page_content}",
                        metadata={
                            **chunk.metadata,
                            "document_id": doc_id,
                            "drive_id": file_id,
                            "file_path": file_path,
                            "context_generated": True,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "processed_at": datetime.utcnow().isoformat()
                        }
                    )
                    processed_chunks.append(contextualized_chunk)
                
                except Exception as chunk_error:
                    # log chunk processing error but continue with others
                    print(f"error processing chunk {i}: {str(chunk_error)}")
                    continue

            if not processed_chunks:
                raise Exception("no chunks were successfully processed")

            # store in vector database
            await self.vector_store.add_documents(processed_chunks)

            # update metadata with success status
            await self.metadata_store.update_status(
                doc_id=doc_id,
                status="completed",
                chunk_count=len(processed_chunks)
            )

            return doc_id

        except Exception as e:
            # update metadata with error status
            if metadata and metadata.document_id:
                await self.metadata_store.update_status(
                    doc_id=metadata.document_id,
                    status="failed",
                    error=str(e)
                )
            raise Exception(f"document processing failed: {str(e)}")

    async def reprocess_failed_chunks(self, doc_id: str) -> bool:
        """REPROCESS FAILED CHUNKS FOR A DOCUMENT"""
        try:
            metadata = await self.metadata_store.get_document(doc_id)
            if not metadata or metadata['processing']['status'] != 'failed':
                return False

            # Attempt to reprocess
            await self.process_file(
                file_id=metadata['original_file']['drive_id'],
                file_path=metadata['original_file']['path']
            )
            return True

        except Exception as e:
            print(f"error reprocessing document {doc_id}: {str(e)}")
            return False

    async def get_processing_status(self, doc_id: str) -> dict:
        """GET CURRENT PROCESSING STATUS OF A DOCUMENT"""
        return await self.metadata_store.get_document(doc_id)