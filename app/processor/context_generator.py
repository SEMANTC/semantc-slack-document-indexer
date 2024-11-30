# app/processor/context_generator.py

from langchain_anthropic import ChatAnthropic

class ContextGenerator:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-latest",
            temperature=0,
        )
        self.context_prompt = """
        <document>
        {doc_content}
        </document>
        here is the chunk we want to situate within the whole document
        <chunk>
        {chunk_content}
        </chunk>
        please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
        answer only with the succinct context and nothing else.
        """
    
    async def generate_context(self, document_content: str, chunk_content: str) -> str:
        """GENERATES CONTEXT FOR A CHUNK USING THE FULL DOCUMENT"""
        response = await self.llm.ainvoke(
            self.context_prompt.format(
                doc_content=document_content,
                chunk_content=chunk_content
            )
        )
        return response.content