"""
API endpoints for document ingestion.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import tempfile
from pathlib import Path
from backend.core.parsers import DocumentParser
from backend.core.rag import RAGPipeline
from backend.core.chunking import TextChunker

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])

# Initialize components (in production, use dependency injection)
parser = DocumentParser()
chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
rag_pipeline = None  # Will be initialized in main.py


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and ingest a document.
    
    Args:
        file: Uploaded file
        
    Returns:
        Status and document info
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    # Save uploaded file temporarily
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Parse document
        result = parser.parse_file(tmp_path)
        
        if not result or not result.get("text"):
            raise HTTPException(status_code=400, detail="No content extracted from document")
        
        # Extract text and metadata
        text = result["text"]
        metadata_dict = result["metadata"]
        
        # Use RecursiveCharacterTextSplitter to chunk the text
        chunks = chunker.chunk_text(text)
        
        # Prepare chunks with metadata
        chunked_docs = [{"text": chunk, "metadata": metadata_dict.copy()} for chunk in chunks]
        
        # Add to RAG pipeline (which adds to vector DB)
        rag_pipeline.add_documents([doc["text"] for doc in chunked_docs], [doc["metadata"] for doc in chunked_docs])
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(chunks),
            "message": f"Successfully ingested {len(chunks)} chunks"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/upload-multiple")
async def upload_multiple_documents(files: List[UploadFile] = File(...)):
    """
    Upload and ingest multiple documents.
    
    Args:
        files: List of uploaded files
        
    Returns:
        Status and summary
    """
    results = []
    for file in files:
        try:
            result = await upload_document(file)
            results.append(result)
        except Exception as e:
            results.append({
                "status": "error",
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "status": "completed",
        "total_files": len(files),
        "results": results
    }


@router.get("/stats")
async def get_ingestion_stats():
    """
    Get statistics about ingested documents.
    
    Returns:
        Database statistics
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    return rag_pipeline.vectordb.get_stats()

