# Universal Context Engine (UCE)

## High-Level Architecture

```
User
    │
    ▼
Frontend (Next.js)
    │
    ▼
FastAPI Backend
    │
    ▼
Retrieval API
    │
    ▼
Semantic Retriever
    │
 ┌──┴───────────────┐
 ▼                  ▼
Embedding Service   Vector Store
 │                  │
 ▼                  ▼
Sentence Transformers   ChromaDB
```

---

## Current Progress

### ✅ Phase 1
- Backend Setup
- Frontend Setup

### ✅ Phase 2
- Knowledge Base
- Upload
- Chunking

### ✅ Phase 2.5
- Professional UI

### ✅ Phase 3

#### Module 1
Embedding Provider

#### Module 2
Vector Store

#### Module 3
Semantic Retriever

#### Module 4
In Progress

---

## Future Phases

- Context Engine
- Decision Engine
- MCP Tool Layer
- Chat Interface
- Multi-Knowledge Base
- Multimodal Support

---

## Engineering Principles

- Clean Architecture
- SOLID
- Dependency Injection
- Provider Pattern
- Factory Pattern
- Modular Design
- Production-ready code