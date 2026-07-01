# Universal Context Engine — Backend

FastAPI backend for the Universal Context Engine with MCP Action Layer.

## Overview

This backend provides the API foundation for the Universal Context Engine platform. Phase 1 includes health checks, configuration management, and project scaffolding for future AI features.

## Folder Structure

```
backend/
├── api/           # API route modules (future)
├── services/      # Business logic services (future)
├── models/        # Pydantic models and schemas (future)
├── main.py        # FastAPI application entry point
├── config.py      # Environment configuration
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment variables:

```bash
cp .env.example .env
```

4. Edit `.env` and add your API keys when needed:

```
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

## Run

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Endpoints

| Method | Path     | Description              |
|--------|----------|--------------------------|
| GET    | `/`      | Application status       |
| GET    | `/health`| Health check             |

## Future Development

- RAG and knowledge base APIs
- ChromaDB integration
- MCP tool connections
- Agent and decision engine logic
- Email and task execution services
