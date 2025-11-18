"""
Embedding generation module for document vectors.
Supports multiple embedding models via HuggingFace transformers.
"""
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """Generate embeddings for text chunks using sentence transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings
        """
        if not texts:
            return np.array([])
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of embedding
        """
        return self.model.encode([text], convert_to_numpy=True)[0]

