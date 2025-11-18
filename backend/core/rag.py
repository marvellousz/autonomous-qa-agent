"""
RAG (Retrieval-Augmented Generation) module for QA.
Combines vector search with LLM generation.
"""
from typing import List, Dict, Optional
import os
from backend.core.vectordb import VectorDB
from backend.core.chunking import TextChunker


class RAGPipeline:
    """RAG pipeline for question answering."""
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        vectordb_path: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            embedding_model: Model name for embeddings
            vectordb_path: Path to vector database
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.vectordb = VectorDB(embedding_model=embedding_model, index_path=vectordb_path)
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    def add_documents(self, texts: List[str], metadata: List[Dict]):
        """
        Add documents to the RAG pipeline.
        
        Args:
            texts: List of text chunks
            metadata: List of metadata dicts
        """
        # Prepare chunks in the format expected by VectorDB
        chunks = []
        for text, meta in zip(texts, metadata):
            chunks.append({
                "text": text,
                "metadata": meta
            })
        
        # Add to vector database (it handles chunking if needed)
        self.vectordb.add_documents(chunks)
    
    def retrieve_context(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: Query string
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata and scores
        """
        # VectorDB.search now accepts text query directly
        results = self.vectordb.search(query, k=k)
        return results
    
    def format_context(self, contexts: List[Dict]) -> str:
        """
        Format retrieved contexts into a prompt-friendly string.
        
        Args:
            contexts: List of context dictionaries
            
        Returns:
            Formatted context string
        """
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
        """
        Generate response using RAG (Retrieval-Augmented Generation).
        
        Args:
            query: User query
            k: Number of chunks to retrieve
            prompt_template: Optional custom prompt template. If None, uses default.
                           Use {query} and {context} as placeholders.
        
        Returns:
            Tuple of (formatted_prompt, retrieved_contexts)
        """
        # Step 1: Embed query and retrieve top chunks
        contexts = self.retrieve_context(query, k=k)
        
        if not contexts:
            raise ValueError("No relevant context found in vector database")
        
        # Step 2: Format context
        context_text = self.format_context(contexts)
        
        # Step 3: Build prompt with query and retrieved context
        if prompt_template is None:
            prompt = f"""Based on the following context documents, please provide a detailed response.

Context Documents:
{context_text}

Query: {query}

Response:"""
        else:
            prompt = prompt_template.format(query=query, context=context_text)
        
        return prompt, contexts
