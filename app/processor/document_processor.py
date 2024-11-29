# app/processor/document_processor.py

from langchain.document_loaders import GoogleDriveLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import CohereEmbeddings

class DocumentProcessor:
    def __init__(self, context_generator: ContextGenerator, vector_store):
        self.context_generator = context_generator
        self.vector_store = vector_store
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
    async def process_document(self, file_path: str):
        # load document
        loader = GoogleDriveLoader(file_path)
        document = loader.load()
        
        # get full document content
        full_content = " ".join([doc.page_content for doc in document])
        
        # split into chunks
        chunks = self.splitter.split_text(full_content)
        
        # generate context for each chunk
        contextualized_chunks = []
        for chunk in chunks:
            context = await self.context_generator.generate_context(
                document_content=full_content,
                chunk_content=chunk
            )
            contextualized_chunks.append(f"{context}\n\n{chunk}")
        
        # store in vector database
        await self.vector_store.aadd_texts(contextualized_chunks)