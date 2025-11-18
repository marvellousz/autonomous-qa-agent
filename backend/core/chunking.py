"""
Text chunking utilities using RecursiveCharacterTextSplitter.
"""
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """Text chunking using RecursiveCharacterTextSplitter."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Maximum size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
            separators: List of separators to use for splitting (default: standard set)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Default separators: try to split on paragraphs, sentences, words
        if separators is None:
            separators = [
                "\n\n",
                "\n",
                ". ",
                "! ",
                "? ",
                "; ",
                ", ",
                " ",
                ""
            ]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        chunks = self.splitter.split_text(text)
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk a list of documents.
        
        Args:
            documents: List of dictionaries with "text" and "metadata" keys
            
        Returns:
            List of chunked documents with same structure
        """
        chunked_docs = []
        
        for doc in documents:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            
            chunks = self.chunk_text(text)
            
            for chunk in chunks:
                chunked_docs.append({
                    "text": chunk,
                    "metadata": metadata.copy()
                })
        
        return chunked_docs

