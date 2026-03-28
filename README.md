# CRAG - Corrective Retrieval-Augmented Generation

![Logo](frontend/public/logo.svg)

<!-- Badges -->
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.2+-red.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![React](https://img.shields.io/badge/React-18.3-61dafb.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-purple.svg)

> **Production-grade AI research agent with intelligent document retrieval, quality grading, and web search fallback powered by PyTorch ML models.**

## Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Production Deployment](#-production-deployment)

## Features

- **Intelligent Document Retrieval**: Vector-based semantic search through local documents using sentence-transformers
- **ML-Powered Quality Grading**: PyTorch neural network classifiers for document relevance assessment
- **Corrective Fallback**: Automatic Brave Search integration when local knowledge is insufficient
- **Answer Quality Assessment**: Built-in ML model evaluates response confidence and quality
- **Semantic Similarity**: Advanced similarity computation for better document ranking
- **Source Citations**: Every answer includes traceable, verifiable sources
- **LangGraph Workflow**: State-machine based processing pipeline for reliability
- **Dual Interfaces**: Modern React web UI + CLI for flexibility
- **Production Ready**: Docker containerization, CORS, rate limiting, comprehensive error handling

## Tech Stack

| Layer | Technology |
|-------|------------|
| **ML Models** | PyTorch, sentence-transformers, transformers |
| **LLM Framework** | LangChain, LangGraph |
| **Embedding** | all-MiniLM-L6-v2 (local) |
| **LLM** | GPT-4o-mini (OpenAI) |
| **Vector DB** | FAISS |
| **Backend API** | FastAPI, uvicorn |
| **Frontend** | React 18, TypeScript, Vite |
| **Document Processing** | unstructured |
| **Web Search** | Brave Search API |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (React Web UI / CLI)                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │   Routers   │  │   Middleware │  │   LangGraph Workflow    │ │
│  │  /query     │  │   CORS,Logs  │  │   ┌─────┐ ┌─────────┐   │ │
│  │  /documents │  │   Rate Limit │  │   │Retrieve│ │Grade   │   │ │
│  │  /health   │  │              │  │   └─────┘ └─────────┘   │ │
│  └─────────────┘  └──────────────┘  │   ┌──────┐ ┌────────┐   │ │
│                                    │   │Web   │ │Generate│   │ │
│                                    │   │Search│ │Answer │   │ │
│                                    │   └──────┘ └────────┘   │ │
│                                    └─────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   FAISS         │  │   Brave Search  │  │   PyTorch ML    │
│   Vector Store  │  │   API           │  │   Models        │
│   (Local Docs)  │  │   (Web Fallback)│  │   (Classifier)  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Workflow

```
User Query
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│  1. RETRIEVE - Vector similarity search in local docs      │
└────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│  2. GRADE - ML classifier scores document relevance        │
└────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────┐        ┌─────────────────────┐
│  < 2 good chunks?   │────YES──│  3. WEB SEARCH      │
└─────────────────────┘        │    Brave Search API │
        │ NO                    └─────────────────────┘
        ▼                               │
┌─────────────────────┐                  │
│  4. GENERATE        │◄─────────────────┘
│  GPT-4o-mini        │
└─────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│  5. RESPONSE - Answer with citations & confidence score    │
└────────────────────────────────────────────────────────────┘
```

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/opeblow/AI-RESEARCH-AGENT.git
cd crag

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Build and run with Docker Compose
docker-compose up --build

# Access the web UI
open http://localhost:3000
```

### Manual Setup

```bash
# 1. Clone and setup environment
git clone https://github.com/opeblow/AI-RESEARCH-AGENT.git
cd crag

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and BRAVE_API_KEY

# 5. Add documents
mkdir -p data
# Place your PDF, DOCX, or TXT files in data/

# 6. Run the backend
python server.py

# 7. In another terminal, run the frontend
cd frontend
npm install
npm run dev
```

## Installation

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher (for frontend development)
- **OpenAI API Key**: [Get one here](https://platform.openai.com/api-keys)
- **Brave Search API Key**: [Get one here](https://brave.com/search/api/)

### Backend Installation

```bash
# Clone repository
git clone https://github.com/opeblow/AI-RESEARCH-AGENT.git
cd crag

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend Installation

```bash
cd frontend
npm install
```

## Configuration

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key
BRAVE_API_KEY=your-brave-search-api-key

# Optional (with defaults)
APP_NAME=CRAG System
DEBUG=false
ENVIRONMENT=development

MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL=all-MiniLM-L6-v2
TEMPERATURE=0.0

VECTORSTORE_PATH=vectorstore
DATA_PATH=data
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=10

GRADE_THRESHOLD=0.7
MIN_RELEVANT_CHUNKS=2

CORS_ORIGINS=http://localhost:3000,http://localhost:5173
LOG_LEVEL=INFO
```

### Getting API Keys

**OpenAI API Key:**
1. Visit [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key

**Brave Search API Key:**
1. Visit [brave.com/search/api](https://brave.com/search/api/)
2. Sign up for API access
3. Get your API key from the dashboard

## Usage

### CLI Interface

```bash
python main.py
```

Example session:
```
======================================================================
CRAG - Corrective Retrieval-Augmented Generation System
======================================================================
Built by Mobolaji Opeyemi Bolatito Obinna
Local PDFs + Brave Search Fallback
======================================================================

Ask me anything: What are the key findings in the Q3 report?

Thinking...

======================================================================
ANSWER:
======================================================================
The Q3 report shows significant growth in revenue...

======================================================================
SOURCES:
======================================================================
  [LOCAL] Q3_2024_Report.pdf

----------------------------------------------------------------------
CRAG System - Corrective Retrieval-Augmented Generation
----------------------------------------------------------------------
```

### Web Interface

Start the servers:

```bash
# Terminal 1: Backend
python server.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

Access at `http://localhost:5173`

### API Endpoints

#### Query the System

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'
```

Response:
```json
{
  "answer": "Machine learning is a subset of...",
  "sources": [
    {"source": "ml_intro.pdf", "type": "local", "title": "Introduction to ML"}
  ],
  "conversation_id": "abc123",
  "model": "gpt-4o-mini",
  "processing_time_ms": 2450.32,
  "confidence": 0.92,
  "retrieved_chunks": 10,
  "used_web_search": false
}
```

#### Health Check

```bash
curl http://localhost:8000/api/health
```

#### Upload Documents

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@document.pdf"
```

#### Rebuild Index

```bash
curl -X POST http://localhost:8000/api/documents/rebuild-index
```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/query` | Process a query through CRAG |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/documents/upload` | Upload and index a document |
| `POST` | `/api/documents/rebuild-index` | Rebuild the entire index |

### Error Handling

All errors return JSON with structure:
```json
{
  "error": "Error description",
  "detail": "Additional details",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Project Structure

```
crag/
├── crag/                      # Main Python package
│   ├── __init__.py
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Configuration management
│   ├── schemas.py            # Pydantic models
│   ├── models.py            # Agent state types
│   ├── prompts.py            # LLM prompt templates
│   ├── agent.py              # LangGraph workflow
│   ├── nodes.py              # Workflow nodes
│   ├── vectorstore.py        # FAISS management
│   ├── document_processor.py # PDF/DOCX processing
│   ├── llm_manager.py        # LLM and chain management
│   ├── search.py             # Brave Search client
│   ├── routers/              # API route handlers
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── query.py
│   │   └── documents.py
│   └── ml/                   # PyTorch ML components
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── relevance_classifier.py
│       │   └── answer_quality_assessor.py
│       └── similarity/
│           ├── __init__.py
│           └── semantic_similarity.py
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── api/             # API client
│   │   ├── types.ts         # TypeScript types
│   │   ├── App.tsx          # Main app
│   │   └── index.css        # Styles
│   ├── public/              # Static assets
│   └── package.json
│
├── data/                     # Document storage
│   └── *.pdf, *.docx, *.txt
│
├── tests/                    # Unit tests
│
├── main.py                  # CLI entry point
├── server.py                # API server entry point
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Backend container
├── .env.example            # Environment template
├── .gitignore
└── README.md
```

## Development

### Running Tests

```bash
# Python tests
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
ruff check crag/

# Frontend linting
cd frontend
npm run lint
```

## Production Deployment

### Docker Production

```bash
# Build for production
docker-compose -f docker-compose.yml up --build

# Run in detached mode
docker-compose up -d
```

### Environment Variables for Production

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Increase rate limiting
API_RATE_LIMIT=1000
```

### Health Checks

The backend includes automatic health checks:
```bash
curl http://localhost:8000/api/health
```

## License

MIT License - Built by Mobolaji Opeyemi Bolatito Obinna

## Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - State machine workflows
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers) - Embedding models
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library

## Support

For issues and feature requests, please open an issue on GitHub.

---

<p align="center">
  Built with love by <strong>Mobolaji Opeyemi Bolatito Obinna</strong>
</p>
