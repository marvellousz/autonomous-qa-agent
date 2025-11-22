"""
Vector DB using FAISS for similarity search.
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
import os
import json
import faiss
from pathlib import Path
from backend.core.embeddings import EmbeddingGenerator


class VectorDB:
    """FAISS vector DB."""
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        index_path: Optional[str] = None
    ):
        """Init vector DB."""
        self.embedding_generator = EmbeddingGenerator(model_name=embedding_model)
        self.dimension = self.embedding_generator.get_dimension()
        self.index_path = index_path or "data/faiss_index"
        self.index = None
        self.metadata = []
        self._initialize_index()
    
    def _initialize_index(self):
        """Init or load FAISS index."""
        # Create dir if needed
        if self.index_path:
            index_dir = os.path.dirname(self.index_path)
            if index_dir:
                os.makedirs(index_dir, exist_ok=True)
        
        # Load existing or create new
        if os.path.exists(f"{self.index_path}.index"):
            self.load()
        else:
            # Create new L2 index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
    
    def add_documents(self, chunks: List[Dict]):
        """Add docs to vector DB."""
        if not chunks:
            return
        
        # Extract texts
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_generator.get_embeddings(texts)
        
        if embeddings.size == 0:
            return
        
        # Add to FAISS
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata with text
        for i, chunk in enumerate(chunks):
            metadata_with_text = {
                "text": chunk["text"],
                **chunk["metadata"]
            }
            self.metadata.append(metadata_with_text)
        
        # Auto-save
        self.persist()
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar docs."""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_generator.get_embedding(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search FAISS
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata) and idx >= 0:
                metadata = self.metadata[idx].copy()
                text = metadata.pop("text", "")
                
                results.append({
                    "text": text,
                    "metadata": metadata,
                    "score": float(dist)
                })
        
        return results
    
    def persist(self):
        """Save vector DB to disk."""
        if self.index is None:
            return
        
        # Save index
        index_file = f"{self.index_path}.index"
        faiss.write_index(self.index, index_file)
        
        # Save metadata
        metadata_file = f"{self.index_path}.metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def load(self):
        """Load vector DB from disk."""
        index_file = f"{self.index_path}.index"
        metadata_file = f"{self.index_path}.metadata.json"
        
        if not os.path.exists(index_file):
            raise FileNotFoundError(f"Index file not found: {index_file}")
        
        # Load index
        self.index = faiss.read_index(index_file)
        
        # Load metadata
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = []
    
    def get_stats(self) -> Dict:
        """Get vector DB stats."""
        return {
            "total_documents": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "index_path": self.index_path,
            "model": self.embedding_generator.model_name
        }
