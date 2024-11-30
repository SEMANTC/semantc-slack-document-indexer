# app/main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from .processor.document_processor import DocumentProcessor
from .database.vector_store import VectorStore
from .database.metadata_store import MetadataStore
from .processor.context_generator import ContextGenerator
from .processor.chunk_processor import ChunkProcessor
from .config.settings import get_settings

# initialize fastapi app
app = FastAPI(
    title="DOCUMENT INDEXER SERVICE",
    description="service for processing and indexing documents from Google Drive",
    version="1.0.0"
)

# load settings
settings = get_settings()

# initialize components
vector_store = VectorStore(settings)
metadata_store = MetadataStore(settings.PROJECT_ID)
context_generator = ContextGenerator()
chunk_processor = ChunkProcessor(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP
)

# initialize document processor
document_processor = DocumentProcessor(
    vector_store=vector_store,
    metadata_store=metadata_store,
    context_generator=context_generator,
    chunk_processor=chunk_processor,
    settings=settings  # Add settings
)

# request models
class ProcessDocumentRequest(BaseModel):
    file_id: str
    
class ProcessResponse(BaseModel):
    document_id: str
    status: str = "processing"
    
class StatusResponse(BaseModel):
    document_id: str
    status: str
    chunk_count: Optional[int] = None
    error: Optional[str] = None

# endpoints
@app.post("/process", response_model=ProcessResponse)
async def process_document(request: ProcessDocumentRequest, background_tasks: BackgroundTasks):
    """
    PROCESS A DOCUMENT FROM GOOGLE DRIVE
    
    args:
        file_id: google drive file id
        
    returns:
        document_id: id of the processed document for status tracking
    """
    try:
        # start processing in background
        doc_id = await document_processor.process_file(file_id=request.file_id)
        return ProcessResponse(document_id=doc_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{doc_id}", response_model=StatusResponse)
async def get_status(doc_id: str):
    """
    GET DOCUMENT PROCESSING STATUS
    
    args:
        doc_id: document id returned from process endpoint
        
    returns:
        status information about the document processing
    """
    try:
        status = await metadata_store.get_document(doc_id)
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Document {doc_id} not found"
            )
        return StatusResponse(**status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# health check endpoint
@app.get("/health")
async def health_check():
    """
    HEALTH CHECK ENDPOINT
    """
    return {"status": "healthy"}

# error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {"error": str(exc)}, 500