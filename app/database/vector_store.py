# app/database/vector_store.py

from langchain_community.vectorstores import Pinecone
from .embeddings import get_embeddings
import pinecone

class VectorStore:
    def __init__(self, settings):
        # initialize pinecone
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        
        # get embeddings instance
        self.embeddings = get_embeddings(settings.OPENAI_API_KEY)
        
        # initialize vector store
        self.index_name = settings.PINECONE_INDEX_NAME
        self.vector_store = Pinecone(
            index=pinecone.Index(self.index_name),
            embedding=self.embeddings,
            text_key="text",
            namespace="default"
        )
    
    async def add_documents(self, documents):
        """ADD DOCUMENTS TO VECTOR STORE"""
        return await self.vector_store.aadd_documents(documents)
    
    async def similarity_search(self, query: str, k: int = 3):
        """SEARCH FOR SIMILAR DOCUMENTS"""
        return await self.vector_store.asimilarity_search(query, k=k)