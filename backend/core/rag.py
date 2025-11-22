"""
RAG pipeline - vector search + LLM generation.
"""
from typing import List, Dict, Optional
import os
from backend.core.vectordb import VectorDB
from backend.core.chunking import TextChunker


class RAGPipeline:
    """RAG for QA."""
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        vectordb_path: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """Init RAG pipeline."""
        self.vectordb = VectorDB(embedding_model=embedding_model, index_path=vectordb_path)
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    def add_documents(self, texts: List[str], metadata: List[Dict]):
        """Add docs to RAG pipeline."""
        chunks = []
        for text, meta in zip(texts, metadata):
            chunks.append({
                "text": text,
                "metadata": meta
            })
        
        self.vectordb.add_documents(chunks)
    
    def retrieve_context(self, query: str, k: int = 5) -> List[Dict]:
        """Get relevant context for query."""
        results = self.vectordb.search(query, k=k)
        return results
    
    def format_context(self, contexts: List[Dict]) -> str:
        """Format contexts for prompt."""
        formatted = []
        for i, ctx in enumerate(contexts, 1):
            source = ctx["metadata"].get("source", "unknown")
            text = ctx["text"]
            formatted.append(f"[Document {i} from {source}]\n{text}\n")
        
        return "\n".join(formatted)
    
    def generate_with_rag(
        self,
        query: str,
        k: int = 5,
        prompt_template: Optional[str] = None
    ) -> tuple[str, List[Dict]]:
        """Generate response using RAG."""
        # Get relevant chunks
        contexts = self.retrieve_context(query, k=k)
        
        if not contexts:
            raise ValueError("No relevant context found in vector database")
        
        # Format context
        context_text = self.format_context(contexts)
        
        # Build prompt
        if prompt_template is None:
            prompt = f"""Based on the following context documents, please provide a detailed response.

Context Documents:
{context_text}

Query: {query}

Response:"""
        else:
            prompt = prompt_template.format(query=query, context=context_text)
        
        return prompt, contexts
