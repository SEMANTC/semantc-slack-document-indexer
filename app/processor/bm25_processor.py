# app/processor/bm25_processor.py
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any
import numpy as np

class BM25Processor:
    def __init__(self):
        self.bm25 = None
        self.corpus = None
        
    def index_documents(self, documents: List[str]):
        """INDEX DOCUMENTS USING BM25"""
        # tokenize documents
        tokenized_corpus = [doc.lower().split() for doc in documents]
        self.corpus = documents
        self.bm25 = BM25Okapi(tokenized_corpus)
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """SEARCH DOCUMENTS USING BM25"""
        if not self.bm25:
            raise Exception("no documents indexed")
            
        # tokenize query
        tokenized_query = query.lower().split()
        
        # get scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # get top k documents
        top_k = np.argsort(scores)[-k:][::-1]
        
        return [
            {
                "document": self.corpus[idx],
                "score": scores[idx]
            }
            for idx in top_k
        ]