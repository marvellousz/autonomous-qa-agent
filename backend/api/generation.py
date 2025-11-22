"""
API endpoints for QA and Selenium script generation.
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
    """LLM wrapper for Ollama/Groq/HuggingFace."""
    
    def __init__(self, provider: str = "ollama", model: str = "llama2"):
        """Init LLM interface."""
        self.provider = provider
        self.model = model
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using LLM."""
        if self.provider == "ollama":
            return self._generate_ollama(prompt, max_tokens)
        elif self.provider == "groq":
            return self._generate_groq(prompt, max_tokens)
        else:
            # Fallback
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
                timeout=120
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            elif response.status_code == 404:
                # Model not found
                available_models = self._get_ollama_models()
                return f"Error: Model '{self.model}' not found. Available models: {', '.join(available_models) if available_models else 'None'}. Please run: ollama pull {self.model}"
            else:
                error_detail = response.text[:200] if hasattr(response, 'text') else str(response.status_code)
                return f"Error: {response.status_code} - {error_detail}"
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Please ensure Ollama is running (run 'ollama serve' in a terminal)."
        except requests.exceptions.Timeout:
            return "Error: Request to Ollama timed out. The model may be too slow or not responding."
        except Exception as e:
            return f"Ollama error: {str(e)}"
    
    def _get_ollama_models(self) -> List[str]:
        """Get available Ollama models."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model.get("name", "") for model in data.get("models", [])]
            return []
        except:
            return []
    
    def _generate_groq(self, prompt: str, max_tokens: int) -> str:
        """Generate using Groq API."""
        # Placeholder - needs API key
        return f"[Groq API call would be made here with prompt: {prompt[:50]}...]"


# Init LLM
llm = LLMInterface(provider="ollama", model="llama2")
rag_pipeline = None  # Set in main.py


class QARequest(BaseModel):
    """QA request."""
    question: str
    context: Optional[str] = None
    max_tokens: int = 500


class SeleniumRequest(BaseModel):
    """Selenium script request."""
    description: str
    url: Optional[str] = None
    actions: Optional[List[str]] = None


class TestCaseRequest(BaseModel):
    """Test case generation request."""
    query: str
    k: int = 5
    max_tokens: int = 2000
    output_format: str = "json"  # json or markdown


class ScriptGenerationRequest(BaseModel):
    """Selenium script generation request."""
    test_case: Dict[str, Any]
    checkout_html: str
    url: Optional[str] = None
    k: int = 5
    max_tokens: int = 3000


@router.post("/qa")
async def generate_answer(request: QARequest):
    """Generate answer using RAG."""
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        # Get context
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
    """Generate Selenium script."""
    try:
        # Build prompt
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
    """Extract IDs, names, and classes from HTML."""
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
    
    # Format selectors
    selectors_info = []
    
    # ID selectors
    for id_val in ids:
        selectors_info.append(f"#id: #{id_val}")
    
    # Name selectors
    for name_val in names:
        selectors_info.append(f"#name: [name='{name_val}']")
    
    # Class selectors (first 20)
    for class_val in classes[:20]:
        selectors_info.append(f"#class: .{class_val}")
    
    return {
        "ids": ids,
        "names": names,
        "classes": classes[:20],
        "selectors": selectors_info
    }


@router.post("/generate_script")
async def generate_script(request: ScriptGenerationRequest):
    """Generate Selenium script from test case and HTML."""
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        # Extract HTML selectors
        selectors = extract_html_selectors(request.checkout_html)
        
        # Get relevant docs
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
        
        # Build prompt
        prompt = f"""You are an expert Selenium Python automation engineer. Generate a production-quality, fully runnable Selenium script.

Test Case Information:
- Test_ID: {test_id}
- Feature: {feature}
- Scenario: {scenario}
- Steps: {steps}
- Expected_Result: {expected_result}

HTML Structure Analysis:
Available IDs: {', '.join(selectors['ids'][:15]) if selectors['ids'] else 'None found'}
Available Names: {', '.join(selectors['names'][:15]) if selectors['names'] else 'None found'}
Available Classes: {', '.join(selectors['classes'][:15]) if selectors['classes'] else 'None found'}

Complete Selector Reference:
{chr(10).join(selectors['selectors'][:30]) if selectors['selectors'] else 'No selectors found'}

Relevant Documentation Context:
{context_text if context_text else "No additional documentation provided."}

CRITICAL REQUIREMENTS FOR SCRIPT QUALITY:
1. Use webdriver.Chrome() for browser initialization
2. Selector Priority: Use IDs first (most reliable), then names, then classes, then CSS selectors
3. Match selectors EXACTLY to the HTML structure provided above
4. Include ALL required imports at the top:
   - from selenium import webdriver
   - from selenium.webdriver.common.by import By
   - from selenium.webdriver.support.ui import WebDriverWait
   - from selenium.webdriver.support import expected_conditions as EC
   - from selenium.webdriver.chrome.service import Service
   - from selenium.webdriver.chrome.options import Options
   - import time (if needed)

5. Use explicit waits (WebDriverWait) for all dynamic elements - DO NOT use time.sleep()
6. Implement proper error handling with try-except-finally blocks
7. Add clear comments explaining each major step
8. Include assertions to verify expected results match the test case
9. Always close the browser in a finally block
10. Handle form validation errors if mentioned in test case
11. Use proper Selenium best practices (no hardcoded waits, proper element location strategies)
12. Make the script immediately runnable - include all necessary code

Test URL: {request.url if request.url else 'https://example.com/checkout'}

Generate the complete, production-ready Python Selenium script. Output ONLY the Python code, no explanations:"""

        # Generate script
        script = llm.generate(prompt, max_tokens=request.max_tokens)
        
        # Clean up script
        script_cleaned = script.strip()
        
        # Remove markdown code blocks
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


def _parse_markdown_test_cases(markdown_text: str, source_documents: List[str]) -> Optional[List[Dict]]:
    """Parse markdown test cases to JSON."""
    if not markdown_text or not isinstance(markdown_text, str):
        return None
    
    try:
        test_cases = []
        current_case = {}
        current_field = None
        steps_list = []
        
        lines = markdown_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse Test_ID
            if line.startswith('Test_ID:'):
                if current_case:
                    if steps_list:
                        current_case['Steps'] = steps_list
                    test_cases.append(current_case)
                current_case = {}
                steps_list = []
                parts = line.split(':', 1)
                if len(parts) > 1:
                    current_case['Test_ID'] = parts[1].strip()
                else:
                    current_case['Test_ID'] = f"TC-{len(test_cases) + 1:03d}"
                # Default Grounded_In
                current_case['Grounded_In'] = source_documents[0] if source_documents else "unknown"
            
            # Parse Feature
            elif line.startswith('Feature:'):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    current_case['Feature'] = parts[1].strip()
            
            # Parse Scenario
            elif line.startswith('Scenario:'):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    current_case['Scenario'] = parts[1].strip()
            
            # Parse Steps
            elif line.startswith('Steps:'):
                current_field = 'steps'
                steps_list = []
            
            # Parse Expected_Result
            elif line.startswith('Expected Result:') or line.startswith('Expected_Result:'):
                if steps_list:
                    current_case['Steps'] = steps_list
                    steps_list = []
                parts = line.split(':', 1)
                if len(parts) > 1:
                    current_case['Expected_Result'] = parts[1].strip()
                current_field = None
            
            # Parse Grounded_In
            elif line.startswith('Grounded In:') or line.startswith('Grounded_In:'):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    grounded = parts[1].strip()
                    # Match source doc
                    for doc in source_documents:
                        if doc.lower() in grounded.lower():
                            current_case['Grounded_In'] = doc
                            break
            
            # Collect steps
            elif current_field == 'steps':
                # Match numbered steps or bullets
                if (re.match(r'^\d+\.', line) or line.startswith(('-', '*'))):
                    step_text = re.sub(r'^\d+\.\s*', '', line)
                    step_text = re.sub(r'^[-*]\s*', '', step_text)
                    if step_text.strip():
                        steps_list.append(step_text.strip())
        
        # Add last test case
        if current_case:
            if steps_list:
                current_case['Steps'] = steps_list
            # Ensure required fields
            if 'Test_ID' not in current_case:
                current_case['Test_ID'] = f"TC-{len(test_cases) + 1:03d}"
            if 'Steps' not in current_case:
                current_case['Steps'] = []
            test_cases.append(current_case)
        
        return test_cases if test_cases else None
    
    except Exception as e:
        import traceback
        print(f"Error parsing markdown: {str(e)}")
        print(traceback.format_exc())
        return None


@router.post("/generate_test_cases")
async def generate_test_cases(request: TestCaseRequest):
    """Generate test cases using RAG."""
    if rag_pipeline is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        # Build prompt template based on requested format
        if request.output_format.lower() == "json":
            prompt_template = """You are a QA test case generation expert. Generate comprehensive test cases STRICTLY based on the provided context documents.

CRITICAL REQUIREMENTS:
1. ALL test cases MUST be grounded in the provided context documents
2. DO NOT invent or hallucinate features not mentioned in the documents
3. Each test case MUST reference the specific document it is based on
4. Use exact values, rules, and specifications from the documents

Context Documents:
{context}

User Query: {query}

CRITICAL INSTRUCTION: You MUST output ONLY valid JSON. NO markdown, NO plain text, NO explanations.

Start your response with [ and end with ]. Output ONLY a JSON array.

Example format (copy this structure exactly):

[
  {{
    "Test_ID": "TC-001",
    "Feature": "Discount Code",
    "Scenario": "Apply valid discount code SAVE15",
    "Steps": ["Step 1", "Step 2", "Step 3"],
    "Expected_Result": "15% discount applied",
    "Grounded_In": "product_specs.md"
  }}
]

REQUIREMENTS:
- Start with [ and end with ]
- Each test case is a JSON object with: Test_ID, Feature, Scenario, Steps (array), Expected_Result, Grounded_In
- Use exact document filenames from context for Grounded_In field
- Generate 3-5 test cases
- Use exact values from documents (SAVE15, $10 shipping, etc.)

Output ONLY the JSON array, nothing else:"""
        else:
            # Markdown format
            prompt_template = """You are a QA test case generation expert. Generate comprehensive test cases STRICTLY based on the provided context documents.

CRITICAL REQUIREMENTS:
1. ALL test cases MUST be grounded in the provided context documents
2. DO NOT invent or hallucinate features not mentioned in the documents
3. Each test case MUST reference the specific document it is based on
4. Use exact values, rules, and specifications from the documents

Context Documents:
{context}

User Query: {query}

Generate test cases in the following format. For each test case, include ALL fields:

Test_ID: TC-XXX (unique identifier)
Feature: [Feature name from documents]
Scenario: [Detailed scenario description]
Steps:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
Expected_Result: [Expected outcome based on documents]
Grounded_In: [Exact document filename from context, e.g., product_specs.md]

IMPORTANT:
- Generate both positive and negative test cases
- Use exact values from documents (e.g., discount codes like SAVE15, prices, validation rules)
- Reference specific document sections when applicable
- Do not create features not mentioned in the provided documents
- Generate 3-5 test cases

Generate the test cases now:"""

        # Generate prompt with RAG
        prompt, contexts = rag_pipeline.generate_with_rag(
            query=request.query,
            k=request.k,
            prompt_template=prompt_template
        )
        
        # Generate test cases
        llm_response = None
        try:
            llm_response = llm.generate(prompt, max_tokens=request.max_tokens)
            print(f"LLM Response (first 500 chars): {llm_response[:500] if llm_response else 'None'}")
        except Exception as e:
            print(f"LLM generation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"LLM generation error: {str(e)}")
        
        if not llm_response:
            raise HTTPException(status_code=500, detail="LLM returned empty response")
        
        # Extract source docs
        source_documents = []
        for ctx in contexts:
            source = ctx["metadata"].get("source", "unknown")
            if source not in source_documents:
                source_documents.append(source)
        
        # Format response
        if request.output_format.lower() == "json":
            json_parsed = False
            try:
                # Clean response
                cleaned_response = llm_response.strip()
                
                # Remove markdown code blocks
                if "```json" in cleaned_response:
                    start_idx = cleaned_response.find("```json")
                    end_idx = cleaned_response.find("```", start_idx + 7)
                    if end_idx != -1:
                        cleaned_response = cleaned_response[start_idx + 7:end_idx].strip()
                    else:
                        cleaned_response = cleaned_response.replace("```json", "").strip()
                elif "```" in cleaned_response:
                    start_idx = cleaned_response.find("```")
                    end_idx = cleaned_response.find("```", start_idx + 3)
                    if end_idx != -1:
                        cleaned_response = cleaned_response[start_idx + 3:end_idx].strip()
                    else:
                        cleaned_response = cleaned_response.replace("```", "").strip()
                
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3].strip()
                
                cleaned_response = cleaned_response.strip()
                print(f"Cleaned response (first 500 chars): {cleaned_response[:500]}")
                
                # Try to find JSON array
                bracket_pos = cleaned_response.find('[')
                if bracket_pos != -1:
                    potential_json = cleaned_response[bracket_pos:]
                    bracket_count = 0
                    end_pos = -1
                    for i, char in enumerate(potential_json):
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_pos = i + 1
                                break
                    
                    if end_pos != -1:
                        json_str = potential_json[:end_pos].strip()
                        json_str = json_str.lstrip('\n\r\t ').rstrip('\n\r\t ')
                        try:
                            parsed_json = json.loads(json_str)
                            if isinstance(parsed_json, list):
                                json_parsed = True
                                return {
                                    "status": "success",
                                    "query": request.query,
                                    "test_cases": parsed_json,
                                    "grounded_in": source_documents,
                                    "sources": [ctx["metadata"] for ctx in contexts]
                                }
                        except (json.JSONDecodeError, ValueError) as e:
                            print(f"JSON array parsing failed: {str(e)}")
                            print(f"JSON string (first 300 chars): {json_str[:300] if 'json_str' in locals() else 'N/A'}")
                
                # Fallback: regex
                json_array_match = re.search(r'\[[\s\S]*?\]', cleaned_response)
                if json_array_match and not json_parsed:
                    try:
                        json_str = json_array_match.group().strip()
                        json_str = json_str.lstrip('\n\r\t ').rstrip('\n\r\t ')
                        parsed_json = json.loads(json_str)
                        if isinstance(parsed_json, list):
                            json_parsed = True
                            return {
                                "status": "success",
                                "query": request.query,
                                "test_cases": parsed_json,
                                "grounded_in": source_documents,
                                "sources": [ctx["metadata"] for ctx in contexts]
                            }
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"JSON array regex parsing failed: {str(e)}")
                        print(f"JSON string (first 300 chars): {json_str[:300] if 'json_str' in locals() else 'N/A'}")
                
                # Try JSON object
                json_object_match = re.search(r'\{[\s\S]*\}', cleaned_response)
                if json_object_match:
                    try:
                        json_str = json_object_match.group().strip()
                        json_str = json_str.lstrip('\n\r\t ').rstrip('\n\r\t ')
                        parsed_json = json.loads(json_str)
                        json_parsed = True
                        return {
                            "status": "success",
                            "query": request.query,
                            "test_cases": parsed_json,
                            "grounded_in": source_documents,
                            "sources": [ctx["metadata"] for ctx in contexts]
                        }
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"JSON object parsing failed: {str(e)}")
                
                # Try parse entire response
                if not json_parsed:
                    try:
                        if not (cleaned_response.startswith('[') or cleaned_response.startswith('{')):
                            json_start = cleaned_response.find('[')
                            json_obj_start = cleaned_response.find('{')
                            if json_start != -1 and (json_obj_start == -1 or json_start < json_obj_start):
                                cleaned_response = cleaned_response[json_start:]
                            elif json_obj_start != -1:
                                cleaned_response = cleaned_response[json_obj_start:]
                        
                        cleaned_response = cleaned_response.lstrip('\n\r\t ').rstrip('\n\r\t ')
                        
                        parsed_json = json.loads(cleaned_response)
                        json_parsed = True
                        return {
                            "status": "success",
                            "query": request.query,
                            "test_cases": parsed_json,
                            "grounded_in": source_documents,
                            "sources": [ctx["metadata"] for ctx in contexts]
                        }
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Full response JSON parsing failed: {str(e)}")
                        print(f"Cleaned response (first 300 chars): {cleaned_response[:300] if 'cleaned_response' in locals() else 'N/A'}")
                
            except Exception as json_error:
                import traceback
                print(f"Unexpected error during JSON parsing: {str(json_error)}")
                print(f"Traceback: {traceback.format_exc()}")
                json_parsed = False
            
            # Fallback to markdown parsing
            if not json_parsed:
                try:
                    print("JSON parsing failed, attempting markdown parsing as fallback...")
                    parsed_markdown = _parse_markdown_test_cases(llm_response, source_documents)
                    if parsed_markdown and len(parsed_markdown) > 0:
                        print(f"Successfully parsed {len(parsed_markdown)} test cases from markdown")
                        return {
                            "status": "success",
                            "query": request.query,
                            "test_cases": parsed_markdown,
                            "grounded_in": source_documents,
                            "sources": [ctx["metadata"] for ctx in contexts],
                            "note": "Converted from markdown format after JSON parsing failed"
                        }
                    else:
                        print("Markdown parsing returned empty or None")
                except Exception as md_error:
                    print(f"Markdown parsing also failed: {str(md_error)}")
                    import traceback
                    print(traceback.format_exc())
                
                # If all parsing fails, return structured format with raw response
                # This allows the frontend to try parsing it
                return {
                    "status": "success",
                    "query": request.query,
                    "test_cases": {
                        "raw_response": llm_response,
                        "format": "markdown",
                        "note": "LLM returned markdown instead of JSON. Frontend will attempt to parse it."
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
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error generating test cases: {error_trace}")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        
        # Always try markdown parsing as fallback if we have the response
        llm_resp = None
        src_docs = []
        ctx_list = []
        
        try:
            llm_resp = llm_response if 'llm_response' in locals() else None
            src_docs = source_documents if 'source_documents' in locals() else []
            ctx_list = contexts if 'contexts' in locals() else []
        except:
            pass
        
        if llm_resp:
            try:
                print("Attempting markdown parsing as fallback...")
                parsed_markdown = _parse_markdown_test_cases(llm_resp, src_docs)
                if parsed_markdown:
                    print(f"Successfully parsed {len(parsed_markdown)} test cases from markdown")
                    return {
                        "status": "success",
                        "query": request.query,
                        "test_cases": parsed_markdown,
                        "grounded_in": src_docs,
                        "sources": [ctx["metadata"] for ctx in ctx_list] if ctx_list else [],
                        "note": "Converted from markdown format after JSON parsing error"
                    }
                else:
                    print("Markdown parsing returned None")
            except Exception as md_error:
                print(f"Markdown parsing also failed: {str(md_error)}")
                import traceback
                print(traceback.format_exc())
        
        # If all else fails, return the raw response with a helpful message
        if llm_resp:
            return {
                "status": "success",
                "query": request.query,
                "test_cases": {
                    "raw_response": llm_resp[:2000] if len(llm_resp) > 2000 else llm_resp,
                    "format": "raw",
                    "note": f"Could not parse as JSON or markdown. Error: {str(e)[:200]}. Showing raw LLM response."
                },
                "grounded_in": src_docs,
                "sources": [ctx["metadata"] for ctx in ctx_list] if ctx_list else []
            }
        
        # Last resort: return raw response instead of raising error
        # This allows the frontend to attempt parsing
        error_msg = str(e)
        requested_format = request.output_format.lower() if hasattr(request, 'output_format') else 'unknown'
        
        # Return a response that the frontend can handle instead of raising an error
        return {
            "status": "success",
            "query": request.query if hasattr(request, 'query') else "",
            "test_cases": {
                "raw_response": llm_resp[:2000] if llm_resp else "No response from LLM",
                "format": "raw",
                "note": f"JSON parsing failed. Error: {error_msg[:200]}. Frontend will attempt markdown parsing."
            },
            "grounded_in": src_docs,
            "sources": [ctx["metadata"] for ctx in ctx_list] if ctx_list else []
        }


@router.get("/providers")
async def get_llm_providers():
    """Get LLM providers."""
    return {
        "providers": ["ollama", "groq", "huggingface"],
        "current": llm.provider,
        "model": llm.model
    }

