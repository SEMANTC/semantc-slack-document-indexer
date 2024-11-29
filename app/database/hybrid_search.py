# app/database/hybrid_search.py

from typing import List, Dict, Any, Optional
import numpy as np
from langchain.schema import Document
from ..processor.embedding_generator import EmbeddingGenerator
from ..processor.bm25_processor import BM25Processor

class HybridSearch:
    """
    IMPLEMENTS HYBRID SEARCH COMBINING SEMANTIC SEARCH (EMBEDDINGS) 
    AND LEXICAL SEARCH (BM25)
    """
    
    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        bm25_processor: BM25Processor,
        alpha: float = 0.5
    ):
        self.embedding_generator = embedding_generator
        self.bm25_processor = bm25_processor
        self.alpha = alpha
        self.documents: Optional[List[Document]] = None
        
    async def index_documents(self, documents: List[Document]):
        """INDEX DOCUMENTS FOR BOTH SEMANTIC AND LEXICAL SEARCH"""
        self.documents = documents
        texts = [doc.page_content for doc in documents]
        
        # index for BM25
        self.bm25_processor.index_documents(texts)
        
        # generate embeddings
        self.embeddings = await self.embedding_generator.generate_embeddings(texts)
    
    async def search(
        self,
        query: str,
        k: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        PERFORM HYBRID SEARCH
        
        args:
            query: search query
            k: number of results to return
            filter_metadata: optional metadata filters
        returns:
            list of results with scores
        """
        if not self.documents:
            raise ValueError("no documents indexed, call index_documents first")
            
        # get semantic search scores
        query_embedding = await self.embedding_generator.generate_query_embedding(query)
        semantic_scores = np.dot(self.embeddings, query_embedding)
        
        # get bm25 scores
        bm25_results = self.bm25_processor.search(query, k=len(self.documents))
        bm25_scores = [result["score"] for result in bm25_results]
        
        # normalize scores
        semantic_scores = self._normalize_scores(semantic_scores)
        bm25_scores = self._normalize_scores(bm25_scores)
        
        # combine scores
        combined_scores = self.alpha * semantic_scores + (1 - self.alpha) * bm25_scores
        
        # apply metadata filters if provided
        if filter_metadata:
            mask = self._apply_metadata_filters(filter_metadata)
            combined_scores = combined_scores * mask
        
        # get top k results
        results = []
        top_k_indices = np.argsort(combined_scores)[-k:][::-1]
        
        for idx in top_k_indices:
            results.append({
                "document": self.documents[idx],
                "score": {
                    "combined": float(combined_scores[idx]),
                    "semantic": float(semantic_scores[idx]),
                    "bm25": float(bm25_scores[idx])
                }
            })
        
        return results
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """NORMALIZE SCORES TO RANGE [0,1]"""
        min_score = np.min(scores)
        max_score = np.max(scores)
        if max_score == min_score:
            return np.ones_like(scores)
        return (scores - min_score) / (max_score - min_score)
    
    def _apply_metadata_filters(self, filters: Dict[str, Any]) -> np.ndarray:
        """APPLY METADATA FILTERS TO DOCUMENTS"""
        mask = np.ones(len(self.documents), dtype=bool)
        for key, value in filters.items():
            for i, doc in enumerate(self.documents):
                if doc.metadata.get(key) != value:
                    mask[i] = False
        return mask