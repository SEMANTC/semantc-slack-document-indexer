# app/processor/document_processor.py

from langchain.document_loaders import GoogleDriveLoader
from typing import List, Optional
from datetime import datetime
from .chunk_processor import ChunkProcessor
from .context_generator import ContextGenerator
from ..database.vector_store import VectorStore
from ..database.metadata_store import MetadataStore

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
        try:
            # create metadata entry
            doc_metadata = await self.metadata_store.create({
                "file_id": file_id,
                "file_path": file_path,
                "status": "processing",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

            # load document
            document = self.loader.load(file_path)

            # Get full document content for context
            full_content = self.chunk_processor.get_document_text(document)

            # Split into chunks
            chunks = await self.chunk_processor.split_document(document)

            # Generate context and store chunks
            processed_chunks = []
            for chunk in chunks:
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
                        "file_id": file_id,
                        "context_generated": True,
                        "chunk_index": len(processed_chunks)
                    }
                )
                processed_chunks.append(contextualized_chunk)

            # Store in vector database
            await self.vector_store.add_documents(processed_chunks)

            # Update metadata
            await self.metadata_store.update(doc_metadata.id, {
                "status": "completed",
                "chunk_count": len(processed_chunks),
                "updated_at": datetime.utcnow()
            })

            return doc_metadata.id

        except Exception as e:
            # Update metadata with error status
            if doc_metadata:
                await self.metadata_store.update(doc_metadata.id, {
                    "status": "failed",
                    "error": str(e),
                    "updated_at": datetime.utcnow()
                })
            raise