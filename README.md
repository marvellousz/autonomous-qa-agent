# Autonomous QA Agent

An intelligent question-answering system with document ingestion, RAG-based QA, and automated Selenium script generation capabilities. This system enables automated test case generation and Selenium script creation from documentation and HTML files.

## Project Overview

The Autonomous QA Agent is a comprehensive solution that combines:
- **Document Processing**: Parse and ingest various document formats (PDF, HTML, JSON, Markdown, TXT)
- **Vector Search**: FAISS-based semantic search for efficient document retrieval
- **RAG Pipeline**: Retrieval-Augmented Generation for context-aware responses
- **Test Case Generation**: Automated test case creation from feature descriptions
- **Selenium Script Generation**: Automated Python Selenium script generation from test cases and HTML

The system uses local HuggingFace embedding models and supports multiple LLM providers (Ollama, Groq) for flexible deployment.

## Features

### Core Capabilities

- **Multi-Format Document Ingestion**
  - Support for PDF, HTML, JSON, Markdown, and plain text files
  - Automatic text extraction and cleaning
  - Metadata preservation

- **Semantic Vector Search**
  - FAISS-based vector database for fast similarity search
  - Local HuggingFace embedding models (all-MiniLM-L6-v2)
  - Persistent storage with automatic indexing

- **RAG-Powered Generation**
  - Retrieval-Augmented Generation for context-aware responses
  - Automatic context retrieval from knowledge base
  - Grounded responses with source attribution

- **Test Case Generation**
  - Automated test case creation from feature descriptions
  - Structured output (JSON/Markdown)
  - Grounded in documentation with source tracking

- **Selenium Script Generation**
  - HTML selector extraction (IDs, names, classes)
  - Automated Python Selenium script generation
  - Runnable scripts with proper error handling

- **Modern Web Interface**
  - Streamlit-based UI with three main pages
  - Real-time status updates
  - Interactive test case and script management

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Streamlit Frontend                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Upload Docs  │  │ Test Case    │  │ Selenium     │         │
│  │   Page       │  │ Generation   │  │ Script Gen   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼────────────────┘
          │                  │                  │
          │ HTTP Requests    │ HTTP Requests    │ HTTP Requests
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼────────────────┐
│         ▼                  ▼                  ▼                │
│                    FastAPI Backend                              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              API Endpoints                               │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │ /build_kb    │  │ /generate_   │  │ /generate_   │  │ │
│  │  │              │  │ test_cases   │  │ script       │  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │ │
│  └─────────┼──────────────────┼──────────────────┼──────────┘ │
│            │                  │                  │            │
│  ┌─────────┼──────────────────┼──────────────────┼──────────┐  │
│  │         ▼                  ▼                  ▼         │  │
│  │              Core Processing Modules                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │  Parsers     │  │  Chunking    │  │     RAG      │  │  │
│  │  │  (PDF/HTML/ │  │  (Recursive  │  │   Pipeline   │  │  │
│  │  │  JSON/MD)   │  │  Character   │  │              │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │  │
│  └─────────┼──────────────────┼──────────────────┼──────────┘  │
│            │                  │                  │            │
│  ┌─────────┼──────────────────┼──────────────────┼──────────┐  │
│  │         ▼                  ▼                  ▼         │  │
│  │              Embedding & Vector Database                 │  │
│  │  ┌──────────────┐              ┌──────────────┐        │  │
│  │  │ Embeddings   │──────────────▶│  Vector DB   │        │  │
│  │  │ (HuggingFace)│              │   (FAISS)    │        │  │
│  │  └──────────────┘              └──────────────┘        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    LLM Interface                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │   Ollama     │  │    Groq      │  │ HuggingFace  │  │  │
│  │  │  (Local)     │  │   (API)      │  │  (Optional)  │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Component Flow

1. **Document Ingestion Flow**:
   ```
   Upload Files → Parser → Text Extraction → Chunking → Embeddings → Vector DB
   ```

2. **Test Case Generation Flow**:
   ```
   Feature Query → Embed Query → Vector Search → Retrieve Context → LLM → Test Cases
   ```

3. **Script Generation Flow**:
   ```
   Test Case + HTML → Extract Selectors → Retrieve Docs → LLM → Selenium Script
   ```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)
- LLM Provider (Ollama recommended for local use)

### Step 1: Clone/Navigate to Project

```bash
cd /path/to/ocean-ai
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (backend server)
- Streamlit (frontend UI)
- FAISS (vector database)
- Sentence Transformers (embeddings)
- PyMuPDF (PDF parsing)
- BeautifulSoup4 (HTML parsing)
- LangChain Text Splitters (text chunking)
- And other dependencies

### Step 4: Set Up LLM Provider

#### Option A: Ollama (Recommended for Local Use)

1. Install Ollama from [https://ollama.ai](https://ollama.ai)

2. Pull a model:
```bash
ollama pull llama2
# Or use a smaller/faster model:
ollama pull mistral
```

3. Start Ollama service:
```bash
ollama serve
```

#### Option B: Groq API

1. Get API key from [https://groq.com](https://groq.com)

2. Set environment variable:
```bash
export GROQ_API_KEY=your_api_key_here
```

3. Update LLM provider in `backend/api/generation.py`:
```python
llm = LLMInterface(provider="groq", model="llama2-70b-4096")
```

### Step 5: Configure Environment Variables (Optional)

Create a `.env` file in the project root:

```bash
API_BASE_URL=http://localhost:8000
VECTORDB_PATH=data/vectordb
GROQ_API_KEY=your_key_here  # If using Groq
```

## How to Run FastAPI Backend

### Method 1: Using Python Script

```bash
cd backend
python main.py
```

### Method 2: Using Uvicorn Directly (Recommended)

From the project root:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Backend is Running

- API will be available at: `http://localhost:8000`
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API Docs (ReDoc): `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

### Backend Endpoints

- `POST /api/ingestion/build_kb` - Build knowledge base from files
- `POST /api/generation/generate_test_cases` - Generate test cases
- `POST /api/generation/generate_script` - Generate Selenium script
- `GET /api/ingestion/stats` - Get vector database statistics
- `GET /health` - Health check endpoint

## How to Run Streamlit Frontend

### Start Streamlit

In a **new terminal** (keep backend running):

```bash
# Make sure you're in the project root
cd /path/to/ocean-ai

# Activate virtual environment (if not already activated)
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Run Streamlit
streamlit run frontend/app.py
```

### Access the UI

- Streamlit UI will be available at: `http://localhost:8501`
- The browser should open automatically
- If not, navigate to the URL manually

### Frontend Pages

1. **Upload Documents** - Upload docs and HTML, build knowledge base
2. **Test Case Generation** - Generate test cases from feature descriptions
3. **Selenium Script Generation** - Generate Selenium scripts from test cases

## Example Usage Flow

### Complete Workflow Example

#### Step 1: Build Knowledge Base

1. **Start Backend**:
   ```bash
   # Terminal 1
   cd backend
   python main.py
   ```

2. **Start Frontend**:
   ```bash
   # Terminal 2
   streamlit run frontend/app.py
   ```

3. **Upload Documents**:
   - Navigate to "Upload Documents" page
   - Upload documentation files (PDF, TXT, MD, JSON)
   - Upload or paste `checkout.html` content
   - Click "Build Knowledge Base"
   - Wait for confirmation message

#### Step 2: Generate Test Cases

1. Navigate to "Test Case Generation" page
2. Enter feature description:
   ```
   Generate test cases for discount code functionality
   ```
3. Select output format (JSON or Markdown)
4. Click "Generate Test Cases"
5. Review generated test cases in collapsible sections
6. Check grounding information (source documents)

#### Step 3: Generate Selenium Script

1. Navigate to "Selenium Script Generation" page
2. Select a test case from the dropdown
3. Verify checkout HTML is available (or paste it)
4. Optionally enter test URL
5. Click "Generate Selenium Script"
6. Review the generated Python script
7. Copy/download the script using the copy button

### Example API Calls

#### Build Knowledge Base

```bash
curl -X POST "http://localhost:8000/api/ingestion/build_kb" \
  -F "files=@sample_support_docs.txt" \
  -F "files=@sample_checkout.html"
```

#### Generate Test Cases

```bash
curl -X POST "http://localhost:8000/api/generation/generate_test_cases" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate test cases for discount code",
    "k": 5,
    "max_tokens": 2000,
    "output_format": "json"
  }'
```

#### Generate Selenium Script

```bash
curl -X POST "http://localhost:8000/api/generation/generate_script" \
  -H "Content-Type: application/json" \
  -d '{
    "test_case": {
      "Test_ID": "TC_001",
      "Feature": "Checkout",
      "Scenario": "Apply discount code",
      "Steps": "1. Enter code\n2. Click apply",
      "Expected_Result": "Discount applied"
    },
    "checkout_html": "<html>...</html>",
    "url": "https://example.com/checkout"
  }'
```

## Explanation of Support Documents

### Sample Files Location

All sample files are located in the `assets/` directory:

```
assets/
├── sample_checkout.html      # Sample checkout page HTML
└── sample_support_docs.txt   # Sample documentation
```

### sample_checkout.html

**Purpose**: Example HTML file representing a checkout page structure.

**Contains**:
- Form elements with IDs, names, and classes
- Input fields for customer information
- Payment method selection
- Submit button

**Usage**:
- Used for HTML selector extraction
- Provides structure for Selenium script generation
- Demonstrates real-world checkout page format

**Key Elements**:
- Form fields: `name`, `email`, `address`, `city`, `zip`
- Payment selector: `payment` dropdown
- Submit button with ID/class selectors

### sample_support_docs.txt

**Purpose**: Sample documentation file for knowledge base testing.

**Contains**:
- Overview of the Autonomous QA Agent system
- Feature descriptions
- Usage instructions
- API endpoint documentation
- Configuration details

**Usage**:
- Test document ingestion pipeline
- Verify text extraction and chunking
- Test RAG-based retrieval
- Ground test cases in documentation

**Content Structure**:
- Markdown-style headers
- Feature lists
- Code examples
- Configuration instructions

### Using Sample Files

1. **For Testing**:
   ```bash
   # Upload both files via UI or API
   # They will be parsed, chunked, and indexed
   ```

2. **For Development**:
   - Modify files to test different document structures
   - Add more complex HTML structures
   - Test edge cases in parsing

3. **For Demos**:
   - Use as example inputs for demonstrations
   - Show complete workflow with real files
   - Validate system functionality

## Video Demo Instructions

### Preparation

1. **Ensure Both Services Running**:
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:8501`

2. **Prepare Sample Files**:
   - Have `sample_checkout.html` ready
   - Have `sample_support_docs.txt` ready
   - Or use your own documentation files

3. **LLM Provider Ready**:
   - Ollama running with model pulled
   - Or Groq API key configured

### Demo Script

#### Part 1: Knowledge Base Setup (2-3 minutes)

1. **Open Streamlit UI** (`http://localhost:8501`)
2. **Navigate to "Upload Documents" page**
3. **Upload Documentation**:
   - Click "Upload documentation files"
   - Select `sample_support_docs.txt` (or multiple files)
   - Show file selection
4. **Upload HTML**:
   - Choose "Upload HTML file" or "Paste HTML content"
   - Upload `sample_checkout.html` or paste content
   - Show HTML preview
5. **Build Knowledge Base**:
   - Click "Build Knowledge Base" button
   - Show loading spinner
   - Display success message with stats
   - Show "Total Documents in KB" metric

#### Part 2: Test Case Generation (2-3 minutes)

1. **Navigate to "Test Case Generation" page**
2. **Enter Feature Description**:
   ```
   Generate test cases for discount code functionality
   ```
3. **Configure Settings**:
   - Show slider for context chunks (set to 5)
   - Select output format (JSON)
4. **Generate Test Cases**:
   - Click "Generate Test Cases" button
   - Show loading spinner
   - Display generated test cases in collapsible sections
   - Expand one test case to show structure:
     - Test_ID
     - Feature
     - Scenario
     - Steps
     - Expected_Result
     - Grounded_In
5. **Show Grounding**:
   - Point out "Grounded in" section
   - Expand "View Sources" to show source documents

#### Part 3: Selenium Script Generation (3-4 minutes)

1. **Navigate to "Selenium Script Generation" page**
2. **Select Test Case**:
   - Show dropdown with generated test cases
   - Select one test case
   - Expand "Selected Test Case Details"
3. **Verify HTML**:
   - Show "Checkout HTML available" message
   - Optionally expand HTML preview
4. **Enter URL** (optional):
   ```
   https://example.com/checkout
   ```
5. **Generate Script**:
   - Click "Generate Selenium Script" button
   - Show loading spinner
   - Display generated Python script in code block
   - Highlight key features:
     - Proper imports
     - WebDriver initialization
     - Selector usage (IDs, names, classes)
     - Error handling
     - Assertions
6. **Copy Script**:
   - Click "Copy Script" button
   - Show download/copy confirmation
7. **Show Metadata**:
   - Point out selector counts
   - Show documentation sources used

### Tips for Recording

1. **Screen Recording Settings**:
   - Record at 1080p minimum
   - Show both browser and terminal (if possible)
   - Use clear, readable fonts

2. **Narration Points**:
   - Explain each step clearly
   - Mention key features as you use them
   - Highlight the RAG pipeline working
   - Show how test cases are grounded in docs

3. **Timing**:
   - Keep demo under 10 minutes total
   - Pause during loading to explain what's happening
   - Speed up repetitive parts in post-production

4. **Highlights**:
   - Emphasize the end-to-end workflow
   - Show how HTML selectors are extracted
   - Demonstrate the quality of generated scripts
   - Point out source attribution (grounding)

### Post-Demo Checklist

- [ ] Verify all features demonstrated
- [ ] Check audio quality
- [ ] Add captions/subtitles if needed
- [ ] Include timestamps for key sections
- [ ] Add intro/outro slides
- [ ] Link to repository in description

## Project Structure

```
ocean-ai/
├── backend/
│   ├── api/
│   │   ├── ingestion.py      # Document upload & KB building endpoints
│   │   └── generation.py      # Test case & script generation endpoints
│   ├── core/
│   │   ├── embeddings.py     # HuggingFace embedding generation
│   │   ├── vectordb.py       # FAISS vector database wrapper
│   │   ├── parsers.py        # Multi-format document parsing
│   │   ├── chunking.py       # RecursiveCharacterTextSplitter
│   │   └── rag.py            # RAG pipeline implementation
│   └── main.py               # FastAPI application entry point
├── frontend/
│   └── app.py                # Streamlit UI application
├── assets/
│   ├── sample_checkout.html  # Sample HTML for testing
│   └── sample_support_docs.txt # Sample documentation
├── data/                     # Generated data directory (auto-created)
│   └── vectordb/            # FAISS index and metadata
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## API Endpoints Reference

### Ingestion Endpoints

- `POST /api/ingestion/build_kb` - Build knowledge base from files
- `POST /api/ingestion/upload` - Upload single document
- `POST /api/ingestion/upload-multiple` - Upload multiple documents
- `GET /api/ingestion/stats` - Get vector database statistics

### Generation Endpoints

- `POST /api/generation/generate_test_cases` - Generate test cases using RAG
- `POST /api/generation/generate_script` - Generate Selenium script
- `POST /api/generation/qa` - Question answering endpoint
- `POST /api/generation/selenium-script` - Legacy script generation
- `GET /api/generation/providers` - List LLM providers

### Utility Endpoints

- `GET /health` - Health check
- `GET /` - API information
- `GET /docs` - Swagger UI documentation

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `VECTORDB_PATH` | Vector DB storage path | `data/vectordb` |
| `GROQ_API_KEY` | Groq API key (if using Groq) | None |

## Troubleshooting

### Common Issues

**Backend won't start**:
- Check if port 8000 is available: `lsof -i :8000`
- Verify all dependencies installed: `pip list`
- Check Python version: `python --version` (need 3.8+)

**Frontend can't connect to backend**:
- Verify backend is running: `curl http://localhost:8000/health`
- Check `API_BASE_URL` environment variable
- Ensure CORS is configured correctly

**LLM errors**:
- For Ollama: Verify `ollama serve` is running
- Check model is pulled: `ollama list`
- Test Ollama: `curl http://localhost:11434/api/generate`
- For Groq: Verify API key is set correctly

**Vector DB errors**:
- Check disk space: `df -h`
- Verify `data/` directory permissions
- Try deleting `data/` and rebuilding KB

**Import errors**:
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`
- Check Python path: `which python`

**Document parsing errors**:
- Verify file format is supported
- Check file encoding (should be UTF-8)
- Ensure file is not corrupted

## Development

### Adding New Document Types

Extend `backend/core/parsers.py`:

```python
def parse_new_format(self, file_path: str) -> Dict:
    # Implementation
    return {
        "text": extracted_text,
        "metadata": {"source": filename, "type": "new_format"}
    }
```

### Customizing LLM Provider

Modify `backend/api/generation.py`:

```python
llm = LLMInterface(provider="your_provider", model="your_model")
```

### Extending RAG Pipeline

Add methods to `backend/core/rag.py`:

```python
def custom_rag_method(self, query: str):
    # Custom RAG logic
    pass
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Acknowledgments

- FastAPI for the backend framework
- Streamlit for the UI framework
- FAISS for vector similarity search
- Sentence Transformers for embeddings
- LangChain for text splitting utilities
