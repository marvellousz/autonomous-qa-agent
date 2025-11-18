"""
API endpoints for QA generation and Selenium script generation.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import re
from bs4 import BeautifulSoup

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


class TestCaseRequest(BaseModel):
    """Request model for test case generation."""
    query: str
    k: int = 5
    max_tokens: int = 2000
    output_format: str = "json"  # "json" or "markdown"


class ScriptGenerationRequest(BaseModel):
    """Request model for Selenium script generation."""
    test_case: Dict[str, Any]  # Selected test case JSON
    checkout_html: str  # Full checkout.html content
    url: Optional[str] = None
    k: int = 5
    max_tokens: int = 3000


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


def extract_html_selectors(html_content: str) -> Dict[str, List[str]]:
    """
    Extract IDs, names, and classes from HTML content.
    
    Args:
        html_content: HTML content as string
        
    Returns:
        Dictionary with 'ids', 'names', 'classes', and 'selectors' (formatted)
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract IDs
    ids = []
    for element in soup.find_all(attrs={"id": True}):
        ids.append(element.get("id"))
    
    # Extract names
    names = []
    for element in soup.find_all(attrs={"name": True}):
        names.append(element.get("name"))
    
    # Extract classes
    classes = []
    for element in soup.find_all(attrs={"class": True}):
        element_classes = element.get("class", [])
        if isinstance(element_classes, list):
            classes.extend(element_classes)
        else:
            classes.append(element_classes)
    
    # Remove duplicates
    ids = list(set(ids))
    names = list(set(names))
    classes = list(set(classes))
    
    # Create formatted selector information
    selectors_info = []
    
    # Add ID selectors
    for id_val in ids:
        selectors_info.append(f"#id: #{id_val}")
    
    # Add name selectors
    for name_val in names:
        selectors_info.append(f"#name: [name='{name_val}']")
    
    # Add class selectors (show first 20 to avoid too much output)
    for class_val in classes[:20]:
        selectors_info.append(f"#class: .{class_val}")
    
    return {
        "ids": ids,
        "names": names,
        "classes": classes[:20],  # Limit to first 20 classes
        "selectors": selectors_info
    }


@router.post("/generate_script")
async def generate_script(request: ScriptGenerationRequest):
    """
    Generate Selenium script from test case and HTML.
    
    Process:
    1. Parse checkout.html to extract IDs/names/classes
    2. Retrieve relevant documentation chunks
    3. Create prompt for LLM
    4. Output final runnable Python script
    
    Args:
        request: Script generation request with test case and HTML
        
    Returns:
        Generated Selenium Python script
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        # Step 1: Parse checkout.html to extract IDs/names/classes
        selectors = extract_html_selectors(request.checkout_html)
        
        # Step 2: Retrieve relevant documentation chunks using test case info
        # Build query from test case
        test_case_query = f"{request.test_case.get('Feature', '')} {request.test_case.get('Scenario', '')}"
        if not test_case_query.strip():
            test_case_query = "Selenium automation testing"
        
        contexts = rag_pipeline.retrieve_context(test_case_query, k=request.k)
        context_text = rag_pipeline.format_context(contexts) if contexts else ""
        
        # Extract test case details
        test_id = request.test_case.get("Test_ID", "TC_001")
        feature = request.test_case.get("Feature", "Checkout")
        scenario = request.test_case.get("Scenario", "")
        steps = request.test_case.get("Steps", "")
        expected_result = request.test_case.get("Expected_Result", "")
        
        # Step 3: Create comprehensive prompt for LLM
        prompt = f"""You are a Selenium Python expert. Generate a complete, runnable Selenium script based on the test case and HTML structure provided.

Test Case Information:
- Test_ID: {test_id}
- Feature: {feature}
- Scenario: {scenario}
- Steps: {steps}
- Expected_Result: {expected_result}

HTML Selectors Available:
IDs: {', '.join(selectors['ids'][:10])}
Names: {', '.join(selectors['names'][:10])}
Classes: {', '.join(selectors['classes'][:10])}

Full Selector List:
{chr(10).join(selectors['selectors'])}

Relevant Documentation:
{context_text if context_text else "No additional documentation provided."}

Requirements:
1. Use webdriver.Chrome() for browser initialization
2. Use correct selectors based on the HTML structure (prefer IDs, then names, then classes)
3. Include proper imports: from selenium import webdriver, from selenium.webdriver.common.by import By, from selenium.webdriver.support.ui import WebDriverWait, from selenium.webdriver.support import expected_conditions as EC
4. Include error handling with try-except blocks
5. Add explicit waits using WebDriverWait where needed
6. Include assertions to verify expected results
7. Add comments explaining each step
8. Close the browser at the end
9. Make the script complete and runnable

URL: {request.url if request.url else 'https://example.com/checkout'}

Generate the complete Python Selenium script:"""

        # Step 4: Generate script using LLM
        script = llm.generate(prompt, max_tokens=request.max_tokens)
        
        # Clean up script - extract code block if present
        script_cleaned = script.strip()
        
        # Remove markdown code block markers if present
        if script_cleaned.startswith("```python"):
            script_cleaned = script_cleaned.replace("```python", "").strip()
        elif script_cleaned.startswith("```"):
            script_cleaned = script_cleaned.replace("```", "").strip()
        
        if script_cleaned.endswith("```"):
            script_cleaned = script_cleaned[:-3].strip()
        
        return {
            "status": "success",
            "test_id": test_id,
            "script": script_cleaned,
            "language": "python",
            "selectors_used": {
                "ids_count": len(selectors['ids']),
                "names_count": len(selectors['names']),
                "classes_count": len(selectors['classes'])
            },
            "sources": [ctx["metadata"] for ctx in contexts] if contexts else []
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(e)}")


@router.post("/generate_test_cases")
async def generate_test_cases(request: TestCaseRequest):
    """
    Generate test cases using RAG.
    
    Process:
    1. Receive user query
    2. Embed query
    3. Retrieve top chunks from vector DB
    4. Send (query + retrieved context) to LLM
    5. Format output as structured Markdown or JSON
    
    Args:
        request: Test case generation request
        
    Returns:
        Generated test cases with grounding metadata
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        # Build prompt template for test case generation
        prompt_template = """Based on the following context documents, generate comprehensive test cases.

Context Documents:
{context}

User Query: {query}

Generate test cases in the following format. For each test case, include:
- Test_ID: A unique identifier
- Feature: The feature being tested
- Scenario: The test scenario description
- Steps: Detailed test steps (numbered list)
- Expected_Result: What should happen
- Grounded_In: The source document name from the context

Ensure all test cases are grounded in the provided context documents."""

        # Use RAG to generate prompt with retrieved context
        prompt, contexts = rag_pipeline.generate_with_rag(
            query=request.query,
            k=request.k,
            prompt_template=prompt_template
        )
        
        # Generate test cases using LLM
        llm_response = llm.generate(prompt, max_tokens=request.max_tokens)
        
        # Extract source documents for grounding
        source_documents = []
        for ctx in contexts:
            source = ctx["metadata"].get("source", "unknown")
            if source not in source_documents:
                source_documents.append(source)
        
        # Format response based on requested format
        if request.output_format.lower() == "json":
            # Try to parse JSON from LLM response, fallback to raw if parsing fails
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                try:
                    parsed_json = json.loads(json_match.group())
                    return {
                        "status": "success",
                        "query": request.query,
                        "test_cases": parsed_json,
                        "grounded_in": source_documents,
                        "sources": [ctx["metadata"] for ctx in contexts]
                    }
                except json.JSONDecodeError:
                    pass
            
            # If JSON parsing fails, return structured format
            return {
                "status": "success",
                "query": request.query,
                "test_cases": {
                    "raw_response": llm_response,
                    "format": "markdown"
                },
                "grounded_in": source_documents,
                "sources": [ctx["metadata"] for ctx in contexts]
            }
        else:
            # Markdown format
            return {
                "status": "success",
                "query": request.query,
                "test_cases": llm_response,
                "format": "markdown",
                "grounded_in": source_documents,
                "sources": [ctx["metadata"] for ctx in contexts]
            }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating test cases: {str(e)}")


@router.get("/providers")
async def get_llm_providers():
    """Get available LLM providers."""
    return {
        "providers": ["ollama", "groq", "huggingface"],
        "current": llm.provider,
        "model": llm.model
    }

