# tests/test_processor/test_document_processor.py

import pytest
from app.processor.document_processor import DocumentProcessor
from app.processor.context_generator import ContextGenerator
from app.processor.chunk_processor import ChunkProcessor

@pytest.mark.asyncio
async def test_process_file(mock_vector_store, mock_metadata_store):
    # setup
    processor = DocumentProcessor(
        vector_store=mock_vector_store,
        metadata_store=mock_metadata_store,
        context_generator=ContextGenerator(),
        chunk_processor=ChunkProcessor()
    )
    
    # test file processing
    doc_id = await processor.process_file(
        file_id="test-file",
        file_path="gs://test-bucket/test.pdf"
    )
    
    # verify metadata was created
    metadata = await mock_metadata_store.get_document(doc_id)
    assert metadata["status"] == "completed"
    
    # verify chunks were stored
    chunks = await mock_vector_store.similarity_search("test query")
    assert len(chunks) > 0