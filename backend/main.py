"""
FastAPI main application for Autonomous QA Agent.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.api import ingestion, generation
from backend.core.rag import RAGPipeline

# Initialize FastAPI app
app = FastAPI(
    title="Autonomous QA Agent API",
    description="API for document ingestion and question answering",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline
vectordb_path = os.getenv("VECTORDB_PATH", "data/vectordb")
os.makedirs(os.path.dirname(vectordb_path), exist_ok=True)

rag_pipeline = RAGPipeline(
    embedding_model="all-MiniLM-L6-v2",
    vectordb_dimension=384,
    vectordb_path=vectordb_path
)

# Make RAG pipeline available to routers
ingestion.rag_pipeline = rag_pipeline
generation.rag_pipeline = rag_pipeline

# Include routers
app.include_router(ingestion.router)
app.include_router(generation.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Autonomous QA Agent API",
        "version": "1.0.0",
        "endpoints": {
            "ingestion": "/api/ingestion",
            "generation": "/api/generation",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    stats = rag_pipeline.vectordb.get_stats()
    return {
        "status": "healthy",
        "vectordb": stats
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
