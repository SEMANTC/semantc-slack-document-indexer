# app/main.py

from fastapi import FastAPI, BackgroundTasks
from typing import Dict
from .processor.document_processor import DocumentProcessor
from .database.vector_store import VectorStore
from .database.metadata_store import MetadataStore
from .processor.context_generator import ContextGenerator
from .processor.chunk_processor import ChunkProcessor
from .config.settings import get_settings

app = FastAPI()
settings = get_settings()

# initialize components
vector_store = VectorStore(settings)
metadata_store = MetadataStore(settings)
context_generator = ContextGenerator(settings)
chunk_processor = ChunkProcessor()

document_processor = DocumentProcessor(
    vector_store=vector_store,
    metadata_store=metadata_store,
    context_generator=context_generator,
    chunk_processor=chunk_processor
)

@app.post("/process")
async def process_document(file_data: Dict[str, str]):
    """
    PROCESS A DOCUMENT FROM GOOGLE DRIVE
    """
    file_id = file_data.get("file_id")
    file_path = file_data.get("file_path")
    
    if not all([file_id, file_path]):
        raise ValueError("missing required file information")
    
    doc_id = await document_processor.process_file(file_id, file_path)
    
    return {"document_id": doc_id}

@app.get("/status/{doc_id}")
async def get_status(doc_id: str):
    """
    GET DOCUMENT PROCESSING STATUS
    """
    return await metadata_store.get_document(doc_id)