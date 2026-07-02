# Universal Context Engine (UCE)

## Project Goal

Universal Context Engine (UCE) is a production-grade AI platform that allows users to upload documents, build knowledge bases, perform semantic retrieval, and later connect external tools using an MCP-inspired architecture.

The project is designed using Clean Architecture and SOLID principles.

---

# Tech Stack

## Backend

- Python
- FastAPI

## Frontend

- Next.js
- TypeScript
- Tailwind CSS

## AI

- Sentence Transformers
- ChromaDB

---

# Current Architecture

Document Upload

↓

Document Extraction

↓

Recursive Chunking

↓

Embedding Service

↓

Vector Store (ChromaDB)

↓

Semantic Retriever

↓

Retrieval API (Current Phase)

↓

Context Engine (Upcoming)

↓

Decision Engine (Upcoming)

↓

Tool Layer (Upcoming)

---

# Completed

## Phase 1

- Backend Setup
- Frontend Setup
- Dashboard

## Phase 2

- Knowledge Base
- PDF Upload
- TXT Upload
- Recursive Chunking
- Metadata

## Phase 2.5

- Better UI
- Upload History
- File Metadata

## Phase 3

### Module 1

Embedding Provider

### Module 2

Vector Store

### Module 3

Semantic Retriever

---

# Engineering Principles

- Clean Architecture
- SOLID Principles
- Dependency Injection
- Provider Pattern
- Factory Pattern
- Production-ready code
- One responsibility per class
- One module per Git commit

---

# Future Roadmap

- Retrieval API
- Context Engine
- Decision Engine
- MCP Tool Layer
- Chat Interface
- Multi-Knowledge Base
- Multimodal Support