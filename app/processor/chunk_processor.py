# app/processor/chunk_processor.py

from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain.docstore.document import Document

class ChunkProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,  # tracks position in original document
        )
    
    async def split_document(self, document: Document) -> List[Document]:
        """SPLIT A DOCUMENT INTO CHUNKS"""
        return self.text_splitter.split_documents([document])

    def get_document_text(self, document: Document) -> str:
        """GET FULL TEXT CONTENT FROM DOCUMENT"""
        return document.page_content