# app/processor/embedding_generator.py

from langchain_openai import OpenAIEmbeddings
from typing import List, Any

class EmbeddingGenerator:
    def __init__(self, api_key: str):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=api_key
        )
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """GENERATE EMBEDDINGS FOR A LIST OF TEXTS"""
        try:
            return await self.embeddings.aembed_documents(texts)
        except Exception as e:
            raise Exception(f"error generating embeddings: {str(e)}")
    
    async def generate_query_embedding(self, text: str) -> List[float]:
        """GENERATE EMBEDDING FOR A SINGLE QUERY"""
        try:
            return await self.embeddings.aembed_query(text)
        except Exception as e:
            raise Exception(f"error generating query embedding: {str(e)}")