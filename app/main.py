# app/main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict
import logging

from .processor.document_processor import DocumentProcessor
from .database.vector_store import VectorStore
from .database.metadata_store import MetadataStore
from .processor.context_generator import ContextGenerator
from .processor.chunk_processor import ChunkProcessor
from .config.settings import get_settings
from .auth.google_auth import GoogleDriveAuth
from .auth.token_storage import TokenStorage
from .models.auth import TokenData, UserAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Document Indexer Service",
    description="Service for processing and indexing documents from Google Drive",
    version="1.0.0"
)

# Load settings
settings = get_settings()

# Initialize components
vector_store = VectorStore(settings)
metadata_store = MetadataStore(settings.PROJECT_ID)
context_generator = ContextGenerator()
chunk_processor = ChunkProcessor(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP
)

# Initialize auth components
google_auth = GoogleDriveAuth(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    redirect_uri=settings.OAUTH_REDIRECT_URI
)
token_storage = TokenStorage(settings.PROJECT_ID)

# Initialize document processor
document_processor = DocumentProcessor(
    vector_store=vector_store,
    metadata_store=metadata_store,
    context_generator=context_generator,
    chunk_processor=chunk_processor,
    settings=settings
)

# Request/Response Models
class ProcessDocumentRequest(BaseModel):
    file_id: str
    user_id: str
    
class ProcessResponse(BaseModel):
    document_id: str
    status: str = "processing"
    
class StatusResponse(BaseModel):
    document_id: str
    status: str
    chunk_count: Optional[int] = None
    error: Optional[str] = None

# Auth Endpoints
@app.get("/auth/google")
async def google_auth_start():
    """Start Google OAuth flow"""
    try:
        auth_url = google_auth.get_authorization_url()
        logger.info(f"Generated auth URL: {auth_url}")
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Auth Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authorization error: {str(e)}")

@app.get("/auth/google/callback")
async def google_auth_callback(code: str, state: Optional[str] = None):
    """Handle OAuth callback"""
    try:
        credentials = google_auth.get_credentials(code)
        # In a real app, you'd get the user_id from the session/token
        user_id = "test_user"
        await token_storage.save_token(user_id, credentials)
        logger.info(f"Successfully saved credentials for user: {user_id}")
        return {"status": "success", "user_id": user_id}
    except Exception as e:
        logger.error(f"Callback Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Document Processing Endpoints
@app.post("/process", response_model=ProcessResponse)
async def process_document(request: ProcessDocumentRequest):
    """Process a document from Google Drive"""
    try:
        # Get user credentials
        credentials = await token_storage.get_token(request.user_id)
        if not credentials:
            raise HTTPException(status_code=401, detail="User not authenticated")

        doc_id = await document_processor.process_file(
            file_id=request.file_id,
            credentials=credentials
        )
        logger.info(f"Started processing document: {doc_id}")
        return ProcessResponse(document_id=doc_id)
        
    except Exception as e:
        logger.error(f"Processing Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{doc_id}", response_model=StatusResponse)
async def get_status(doc_id: str):
    """Get document processing status"""
    try:
        status = await metadata_store.get_document(doc_id)
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Document {doc_id} not found"
            )
        return StatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Status Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {str(exc)}")
    return {"error": str(exc)}, 500