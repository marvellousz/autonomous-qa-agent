"""
API endpoints for QA generation and Selenium script generation.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import os

router = APIRouter(prefix="/api/generation", tags=["generation"])

# LLM interface - supports multiple providers
class LLMInterface:
    """Interface for LLM providers (Groq/Ollama/HuggingFace)."""
    
    def __init__(self, provider: str = "ollama", model: str = "llama2"):
        """
        Initialize LLM interface.
        
        Args:
            provider: LLM provider (ollama, groq, huggingface)
            model: Model name
        """
        self.provider = provider
        self.model = model
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate text using LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        if self.provider == "ollama":
            return self._generate_ollama(prompt, max_tokens)
        elif self.provider == "groq":
            return self._generate_groq(prompt, max_tokens)
        else:
            # Fallback to simple response
            return f"[LLM Response for: {prompt[:50]}...]"
    
    def _generate_ollama(self, prompt: str, max_tokens: int) -> str:
        """Generate using Ollama."""
        try:
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": max_tokens}
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Ollama error: {str(e)}"
    
    def _generate_groq(self, prompt: str, max_tokens: int) -> str:
        """Generate using Groq API."""
        # Placeholder - requires API key
        return f"[Groq API call would be made here with prompt: {prompt[:50]}...]"


# Initialize LLM (in production, use dependency injection)
llm = LLMInterface(provider="ollama", model="llama2")
rag_pipeline = None  # Will be initialized in main.py


class QARequest(BaseModel):
    """Request model for QA generation."""
    question: str
    context: Optional[str] = None
    max_tokens: int = 500


class SeleniumRequest(BaseModel):
    """Request model for Selenium script generation."""
    description: str
    url: Optional[str] = None
    actions: Optional[List[str]] = None


@router.post("/qa")
async def generate_answer(request: QARequest):
    """
    Generate answer to a question using RAG.
    
    Args:
        request: QA request with question and optional context
        
    Returns:
        Generated answer
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        # Retrieve relevant context
        contexts = rag_pipeline.retrieve_context(request.question, k=5)
        context_text = rag_pipeline.format_context(contexts)
        
        # Build prompt
        prompt = f"""Based on the following context, answer the question.

Context:
{context_text}

Question: {request.question}

Answer:"""
        
        # Generate answer
        answer = llm.generate(prompt, max_tokens=request.max_tokens)
        
        return {
            "question": request.question,
            "answer": answer,
            "sources": [ctx["metadata"] for ctx in contexts],
            "context_used": len(contexts) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@router.post("/selenium-script")
async def generate_selenium_script(request: SeleniumRequest):
    """
    Generate Selenium script based on description.
    
    Args:
        request: Request with description and optional URL/actions
        
    Returns:
        Generated Selenium script
    """
    try:
        # Build prompt for script generation
        prompt = f"""Generate a Selenium Python script for the following task:

Description: {request.description}
{f'URL: {request.url}' if request.url else ''}
{f'Actions: {", ".join(request.actions)}' if request.actions else ''}

Generate a complete, runnable Selenium script with proper imports and error handling."""
        
        script = llm.generate(prompt, max_tokens=1000)
        
        return {
            "description": request.description,
            "script": script,
            "language": "python"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(e)}")


@router.get("/providers")
async def get_llm_providers():
    """Get available LLM providers."""
    return {
        "providers": ["ollama", "groq", "huggingface"],
        "current": llm.provider,
        "model": llm.model
    }

