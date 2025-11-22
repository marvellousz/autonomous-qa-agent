"""
FastAPI backend for QA agent.
"""
import sys
from pathlib import Path

# Fix imports
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

load_dotenv()

from backend.api import ingestion, generation
from backend.core.rag import RAGPipeline

# Setup FastAPI app
app = FastAPI(
    title="Autonomous QA Agent API",
    description="API for document ingestion and question answering",
    version="1.0.0"
)

# CORS config (change in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init RAG pipeline
vectordb_path = os.getenv("VECTORDB_PATH", "data/vectordb")
os.makedirs(os.path.dirname(vectordb_path), exist_ok=True)

rag_pipeline = RAGPipeline(
    embedding_model="all-MiniLM-L6-v2",
    vectordb_path=vectordb_path
)

# Share RAG pipeline with routers
ingestion.rag_pipeline = rag_pipeline
generation.rag_pipeline = rag_pipeline

# Add routers
app.include_router(ingestion.router)
app.include_router(generation.router)


@app.get("/")
async def root():
    """API root."""
    return {
        "message": "Autonomous QA Agent API",
        "version": "1.0.0",
        "endpoints": {
            "ingestion": "/api/ingestion",
            "build_kb": "/api/ingestion/build_kb",
            "clear_kb": "/api/ingestion/clear",
            "stats": "/api/ingestion/stats",
            "generation": "/api/generation",
            "generate_test_cases": "/api/generation/generate_test_cases",
            "generate_script": "/api/generation/generate_script",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check."""
    stats = rag_pipeline.vectordb.get_stats()
    return {
        "status": "healthy",
        "vectordb": stats
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
