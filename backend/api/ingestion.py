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


@router.post("/build_kb")
async def build_knowledge_base(files: List[UploadFile] = File(...)):
    """
    Build knowledge base from uploaded files (docs + HTML).
    
    Process:
    1. Receive uploaded files (docs + HTML)
    2. Parse all files → clean text
    3. Chunk text
    4. Generate embeddings
    5. Store in vector database
    
    Args:
        files: List of uploaded files (PDF, HTML, JSON, TXT, MD)
        
    Returns:
        JSON response with status
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    temp_files = []
    all_chunks = []
    
    try:
        # Process each file
        for file in files:
            # Save uploaded file temporarily
            suffix = Path(file.filename).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_path = tmp_file.name
                temp_files.append(tmp_path)
            
            try:
                # Step 1 & 2: Parse file → clean text
                result = parser.parse_file(tmp_path)
                
                if not result or not result.get("text"):
                    continue  # Skip files with no content
                
                # Extract text and metadata
                text = result["text"]
                metadata_dict = result["metadata"]
                
                # Step 3: Chunk text
                chunks = chunker.chunk_text(text)
                
                # Prepare chunks with metadata
                for chunk in chunks:
                    all_chunks.append({
                        "text": chunk,
                        "metadata": metadata_dict.copy()
                    })
            
            except Exception as e:
                # Log error but continue processing other files
                print(f"Error processing {file.filename}: {str(e)}")
                continue
        
        if not all_chunks:
            raise HTTPException(status_code=400, detail="No content extracted from any files")
        
        # Step 4 & 5: Generate embeddings and store in vector database
        # The VectorDB.add_documents handles embedding generation internally
        rag_pipeline.vectordb.add_documents(all_chunks)
        
        # Step 6: Return success response
        return {
            "status": "KB Built Successfully",
            "files_processed": len(files),
            "total_chunks": len(all_chunks)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building knowledge base: {str(e)}")
    finally:
        # Clean up temp files
        for tmp_path in temp_files:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass


@router.delete("/clear")
async def clear_knowledge_base():
    """
    Clear the entire knowledge base (vector database).
    
    Returns:
        Status message
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        # Get stats before clearing
        stats_before = rag_pipeline.vectordb.get_stats()
        total_docs = stats_before.get("total_documents", 0)
        
        if total_docs == 0:
            return {
                "status": "success",
                "message": "Knowledge base is already empty",
                "documents_cleared": 0
            }
        
        # Clear the vector database
        index_path = rag_pipeline.vectordb.index_path
        
        # Remove index file
        index_file = f"{index_path}.index"
        if os.path.exists(index_file):
            os.unlink(index_file)
        
        # Remove metadata file
        metadata_file = f"{index_path}.metadata.json"
        if os.path.exists(metadata_file):
            os.unlink(metadata_file)
        
        # Reinitialize empty index
        rag_pipeline.vectordb._initialize_index()
        
        return {
            "status": "success",
            "message": "Knowledge base cleared successfully",
            "documents_cleared": total_docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing knowledge base: {str(e)}")


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

