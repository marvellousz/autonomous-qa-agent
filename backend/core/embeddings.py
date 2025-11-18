"""
Embedding generation module using local HuggingFace models.
"""
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """Generate embeddings for text using local HuggingFace models."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: HuggingFace model name for embeddings (default: all-MiniLM-L6-v2)
        """
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of embedding vector
        """
        if not text or not text.strip():
            # Return zero vector if text is empty
            return np.zeros(self.model.get_sentence_embedding_dimension())
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def get_embeddings(self, texts: list[str]) -> np.ndarray:
        """
        Get embeddings for multiple texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings (n x dimension)
        """
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.model.get_sentence_embedding_dimension()
