"""
Vector database module for storing and retrieving document embeddings.
Supports both FAISS and ChromaDB backends.
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
import os
import json
import faiss
from pathlib import Path


class VectorDB:
    """Vector database using FAISS for similarity search."""
    
    def __init__(self, dimension: int = 384, index_path: Optional[str] = None):
        """
        Initialize the vector database.
        
        Args:
            dimension: Dimension of embeddings (default: 384 for all-MiniLM-L6-v2)
            index_path: Optional path to save/load FAISS index
        """
        self.dimension = dimension
        self.index_path = index_path or "data/faiss_index"
        self.index = None
        self.metadata = []
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load FAISS index."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        if os.path.exists(f"{self.index_path}.index"):
            self.index = faiss.read_index(f"{self.index_path}.index")
            self._load_metadata()
        else:
            # Use L2 distance (Euclidean)
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def _load_metadata(self):
        """Load metadata associated with vectors."""
        metadata_path = f"{self.index_path}.metadata.json"
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
    
    def _save_metadata(self):
        """Save metadata associated with vectors."""
        metadata_path = f"{self.index_path}.metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f)
    
    def add_documents(self, embeddings: np.ndarray, metadata: List[Dict]):
        """
        Add documents to the vector database.
        
        Args:
            embeddings: numpy array of embeddings (n x dimension)
            metadata: List of metadata dicts for each embedding
        """
        if self.index.ntotal == 0:
            self.index.add(embeddings.astype('float32'))
        else:
            self.index.add(embeddings.astype('float32'))
        
        self.metadata.extend(metadata)
        self._save_metadata()
        self._save_index()
    
    def _save_index(self):
        """Save FAISS index to disk."""
        faiss.write_index(self.index, f"{self.index_path}.index")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of tuples (metadata, distance)
        """
        if self.index.ntotal == 0:
            return []
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(dist)))
        
        return results
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector database."""
        return {
            "total_documents": self.index.ntotal,
            "dimension": self.dimension,
            "index_path": self.index_path
        }

