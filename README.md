# Ocean AI - Autonomous QA Agent

AI-powered QA system that generates test cases and Selenium scripts from docs. No cap, it's actually useful.

## What It Does

- **Ingest docs** → PDF, HTML, JSON, MD, TXT → Builds a knowledge base
- **RAG-powered** → Generates test cases grounded in your docs (no hallucinations)
- **Auto Selenium scripts** → Converts test cases into runnable Python scripts
- **Streamlit UI** → Clean interface, no CLI nonsense

## Quick Start

### Prerequisites
- Python 3.8+
- Ollama (or Groq API key)

### Setup

```bash
# Clone and enter
cd ocean-ai

# Virtual env (you know the drill)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install deps
pip install -r requirements.txt
```

### Run It

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
# Runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend/app.py
# Opens http://localhost:8501
```

### LLM Setup

**Ollama (recommended):**
```bash
ollama pull llama2  # or mistral
ollama serve
```

**Groq (alternative):**
```bash
export GROQ_API_KEY=your_key
# Update backend/api/generation.py to use "groq"
```

## How to Use

1. **Upload Docs** → Upload your docs + `checkout.html` → Click "Build Knowledge Base"
2. **Generate Test Cases** → Enter feature description → Get grounded test cases
3. **Generate Scripts** → Select test case → Get runnable Selenium Python script

## Project Structure

```
ocean-ai/
├── backend/          # FastAPI backend
│   ├── api/         # Endpoints
│   ├── core/        # RAG, embeddings, parsers
│   └── main.py      # Entry point
├── frontend/         # Streamlit UI
├── assets/          # Sample files
└── data/            # Vector DB (auto-created)
```

## Key Features

### Document Processing
- Multi-format parsing (PDF, HTML, JSON, MD, TXT)
- FAISS vector DB with HuggingFace embeddings
- Recursive text chunking with metadata

### RAG Pipeline
- Semantic search for context retrieval
- Grounded responses with source attribution
- Supports Ollama, Groq, HuggingFace

### Test Case Generation
- Structured output (JSON/Markdown)
- Grounded_In field shows source docs
- No hallucination (strict grounding)

### Selenium Script Generation
- Extracts HTML selectors (IDs, names, classes)
- Production-quality Python scripts
- Proper error handling & waits

## API Endpoints

- `POST /api/ingestion/build_kb` - Build knowledge base
- `POST /api/generation/generate_test_cases` - Generate test cases
- `POST /api/generation/generate_script` - Generate Selenium script
- `GET /api/ingestion/stats` - Get KB stats
- `GET /health` - Health check

## Sample Files

Located in `assets/`:
- `checkout.html` - E-Shop checkout page with all features
- `product_specs.md` - Product specs (discount codes, shipping rules)
- `ui_ux_guide.txt` - UI/UX guidelines
- `api_endpoints.json` - API documentation

**Key examples in docs:**
- "The discount code SAVE15 applies a 15% discount"
- "Express shipping costs $10; Standard shipping is free"
- "Form validation errors must be displayed in red text"

## Requirements Met

- Document ingestion (Phase 1)
- Test case generation with RAG (Phase 2)
- Selenium script generation (Phase 3)
- Grounded_In field in all test cases
- No hallucinations (strict grounding)
- Runnable, production-quality scripts
- Complete checkout.html with all features
- Support docs with exact examples

## Troubleshooting

**Backend won't start?**
- Check port 8000: `lsof -i :8000`
- Verify Python 3.8+: `python --version`

**Frontend can't connect?**
- Make sure backend is running: `curl http://localhost:8000/health`
- Check CORS settings

**LLM errors?**
- Ollama: Verify `ollama serve` is running
- Check model: `ollama list`
- Groq: Verify API key is set

**Vector DB issues?**
- Delete `data/` folder and rebuild KB
- Check disk space and permissions

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **Vector DB**: FAISS
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Parsing**: PyMuPDF, BeautifulSoup4
- **LLM**: Ollama/Groq/HuggingFace

## License

MIT License - do whatever you want with it

---

**TL;DR**: Upload docs → Build KB → Generate test cases → Generate Selenium scripts. All grounded in your docs, no BS.
