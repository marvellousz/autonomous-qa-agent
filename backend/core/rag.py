"""
RAG (Retrieval-Augmented Generation) module for QA.
Combines vector search with LLM generation.
"""
from typing import List, Dict, Optional
import os
from backend.core.embeddings import EmbeddingGenerator
from backend.core.vectordb import VectorDB


class RAGPipeline:
    """RAG pipeline for question answering."""
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        vectordb_dimension: int = 384,
        vectordb_path: Optional[str] = None
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            embedding_model: Model name for embeddings
            vectordb_dimension: Dimension of embeddings
            vectordb_path: Path to vector database
        """
        self.embedding_generator = EmbeddingGenerator(model_name=embedding_model)
        self.vectordb = VectorDB(dimension=vectordb_dimension, index_path=vectordb_path)
    
    def add_documents(self, texts: List[str], metadata: List[Dict]):
        """
        Add documents to the RAG pipeline.
        
        Args:
            texts: List of text chunks
            metadata: List of metadata dicts
        """
        embeddings = self.embedding_generator.generate_embeddings(texts)
        self.vectordb.add_documents(embeddings, metadata)
    
    def retrieve_context(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: Query string
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        query_embedding = self.embedding_generator.generate_embedding(query)
        results = self.vectordb.search(query_embedding, k=k)
        
        return [
            {
                "text": result[0].get("text", ""),
                "metadata": result[0],
                "score": result[1]
            }
            for result in results
        ]
    
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

