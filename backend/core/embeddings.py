"""
Embedding gen using HuggingFace models.
"""
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """Generate embeddings for text."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Init embedding generator."""
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for single text."""
        if not text or not text.strip():
            # Return zero vector if empty
            return np.zeros(self.model.get_sentence_embedding_dimension())
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def get_embeddings(self, texts: list[str]) -> np.ndarray:
        """Get embeddings for multiple texts."""
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()
