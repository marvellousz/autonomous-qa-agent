# Autonomous QA Agent

An intelligent question-answering system with document ingestion, RAG-based QA, and Selenium script generation capabilities.

## Features

- **Document Ingestion**: Support for PDF, HTML, JSON, and text files
- **Vector Search**: FAISS-based similarity search for document retrieval
- **Question Answering**: RAG-powered QA using LLM (Ollama/Groq/HuggingFace)
- **Selenium Script Generator**: Generate automation scripts from descriptions
- **Modern UI**: Streamlit-based web interface

## Project Structure

```
ocean-ai/
├── backend/
│   ├── api/
│   │   ├── ingestion.py      # Document upload endpoints
│   │   └── generation.py      # QA and script generation endpoints
│   ├── core/
│   │   ├── embeddings.py      # Embedding generation
│   │   ├── vectordb.py        # FAISS vector database
│   │   ├── parsers.py         # Document parsing (PDF/HTML/JSON)
│   │   └── rag.py             # RAG pipeline
│   └── main.py                # FastAPI application
├── frontend/
│   └── app.py                 # Streamlit UI
├── assets/
│   ├── sample_checkout.html   # Sample HTML document
│   └── sample_support_docs.txt # Sample text document
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Configuration

### LLM Provider Setup

The system supports multiple LLM providers:

**Ollama** (Local, Recommended):
```bash
# Install Ollama from https://ollama.ai
# Pull a model:
ollama pull llama2
```

**Groq** (API):
- Set environment variable: `GROQ_API_KEY=your_key`

**HuggingFace**:
- Configure in `backend/api/generation.py`

## Running the Application

### 1. Start the Backend (FastAPI)

```bash
cd backend
python main.py
```

Or using uvicorn directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 2. Start the Frontend (Streamlit)

In a new terminal:
```bash
streamlit run frontend/app.py
```

The UI will be available at `http://localhost:8501`

## Usage

1. **Ingest Documents**:
   - Navigate to "Document Ingestion" in the sidebar
   - Upload PDF, HTML, JSON, or text files
   - Click "Ingest Documents"

2. **Ask Questions**:
   - Go to "Question Answering"
   - Enter your question
   - Click "Get Answer"

3. **Generate Selenium Scripts**:
   - Go to "Selenium Script Generator"
   - Describe your automation task
   - Optionally provide URL and actions
   - Click "Generate Script"

## API Endpoints

### Ingestion
- `POST /api/ingestion/upload` - Upload single document
- `POST /api/ingestion/upload-multiple` - Upload multiple documents
- `GET /api/ingestion/stats` - Get database statistics

### Generation
- `POST /api/generation/qa` - Generate answer to question
- `POST /api/generation/selenium-script` - Generate Selenium script
- `GET /api/generation/providers` - List available LLM providers

### Health
- `GET /health` - Health check
- `GET /` - API information

## Environment Variables

Optional environment variables:
- `API_BASE_URL`: Backend API URL (default: `http://localhost:8000`)
- `VECTORDB_PATH`: Path for vector database storage (default: `data/vectordb`)
- `GROQ_API_KEY`: Groq API key (if using Groq)

## Development

### Project Structure Details

- **Backend**: FastAPI application with modular API and core components
- **Frontend**: Streamlit single-page application with multiple views
- **Core Modules**: Reusable components for embeddings, vector DB, parsing, and RAG

### Adding New Document Types

Extend `backend/core/parsers.py` to add support for new file formats.

### Customizing LLM Provider

Modify `backend/api/generation.py` to add support for additional LLM providers.

## Troubleshooting

- **Import errors**: Ensure all dependencies are installed and virtual environment is activated
- **LLM errors**: Verify your LLM provider is running and accessible
- **Vector DB errors**: Check disk space and permissions for `data/` directory
- **CORS errors**: Update CORS settings in `backend/main.py` if accessing from different origins

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

