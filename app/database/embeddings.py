# app/database/embeddings.py

from langchain_openai import OpenAIEmbeddings

def get_embeddings(api_key: str = None):
    """
    CREATE AND CONFIGURE OPENAI EMBEDDINGS INSTANCE
    """
    return OpenAIEmbeddings(
        model="text-embedding-3-large",  # latest model
        openai_api_key=api_key,
        chunk_size=1000,  # process 1000 texts at a time when batching
        max_retries=3,    # retry failed requests up to 3 times
    )