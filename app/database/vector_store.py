# app/database/vector_store.py

from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class VectorStore:
    def __init__(self, settings):
        """Initialize vector store with Pinecone"""
        self.settings = settings
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-large"
        )
        
        # Initialize Pinecone client
        self.pc = PineconeClient(api_key=settings.PINECONE_API_KEY)
        
        # Setup index
        self.index = self.setup_pinecone_index()
        
        # Initialize vector store
        self.vector_store = Pinecone(
            index=self.index,
            embedding=self.embeddings,
            text_key="text",
            namespace="default"
        )

    def setup_pinecone_index(self):
        """Setup Pinecone index"""
        try:
            # List existing indexes
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            # Create index if it doesn't exist
            if self.settings.PINECONE_INDEX_NAME not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.settings.PINECONE_INDEX_NAME}")
                self.pc.create_index(
                    name=self.settings.PINECONE_INDEX_NAME,
                    dimension=1536,  # OpenAI embeddings dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.settings.PINECONE_ENVIRONMENT
                    )
                )
            
            # Get the index
            return self.pc.Index(self.settings.PINECONE_INDEX_NAME)
            
        except Exception as e:
            logger.error(f"Error setting up Pinecone index: {str(e)}")
            raise

    async def add_documents(self, documents):
        """Add documents to vector store"""
        try:
            return await self.vector_store.aadd_documents(documents)
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise

    async def similarity_search(self, query: str, k: int = 3):
        """Search for similar documents"""
        try:
            return await self.vector_store.asimilarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise