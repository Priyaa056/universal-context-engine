# Universal Context Engine with MCP Action Layer



An AI platform for knowledge base creation, tool connections, context building, and action execution.



**Phase 1** established the project foundation: FastAPI backend scaffolding, Next.js dashboard UI, navigation, reusable components, and API health endpoints.



**Phase 2** adds Knowledge Base document upload and processing: file validation, text extraction, chunking, and document listing. Embeddings and vector search are planned for Phase 3.



---



## Project Overview



The Universal Context Engine will eventually support:



- **Knowledge Base Creation** — Upload and index documents for contextual retrieval

- **Tool Connections** — Connect MCP-compatible tools for action execution

- **Context Building** — Assemble relevant context from knowledge and tools

- **Action Execution** — Run automated tasks via connected tools



---



## Folder Structure



```

Universal-Context-Engine/

├── frontend/                 # Next.js 15 dashboard

│   ├── app/                  # App Router pages

│   ├── components/           # Layout and UI components

│   ├── lib/                  # API client and utilities

│   ├── types/                # TypeScript interfaces

│   └── package.json

├── backend/                  # FastAPI API

│   ├── api/                  # Route modules (kb.py)

│   ├── services/             # Document and chunking logic

│   ├── models/               # Pydantic schemas

│   ├── uploads/              # Uploaded document files

│   ├── data/                 # documents.json and chunks.json

│   ├── main.py               # Application entry point

│   ├── config.py             # Environment configuration

│   └── requirements.txt

└── README.md

```



---



## Prerequisites



- **Node.js** 18+ and npm

- **Python** 3.11+

- **pip** and virtual environment support



---



## Installation



Clone or navigate to the project directory:



```bash

cd Universal-Context-Engine

```



---



## Frontend Setup



```bash

cd frontend

npm install

```



### Run Frontend



```bash

npm run dev

```



The dashboard runs at [http://localhost:3000](http://localhost:3000).



---



## Backend Setup



```bash

cd backend

python -m venv venv

```



Activate the virtual environment:



```bash

# Windows

venv\Scripts\activate



# Linux / macOS

source venv/bin/activate

```



Install dependencies:



```bash

pip install -r requirements.txt

```



Copy environment variables:



```bash

# Windows

copy .env.example .env



# Linux / macOS

cp .env.example .env

```



Edit `.env` and add API keys when needed:



```

OPENAI_API_KEY=your_key_here

GEMINI_API_KEY=your_key_here

```



### Run Backend



```bash

uvicorn main:app --reload

```



The API runs at [http://127.0.0.1:8000](http://127.0.0.1:8000).



---



## Phase 2 — Knowledge Base Upload



### How to Upload a Document



1. Start the backend (`uvicorn main:app --reload`) and frontend (`npm run dev`).

2. Open [http://localhost:3000/knowledge-base](http://localhost:3000/knowledge-base).

3. Click the upload area or **Browse Files** and select a PDF or TXT file.

4. Click **Upload File**.

5. On success, the document appears in the **Uploaded Documents** list with its chunk count.



### Supported File Types



| Format | Extension | Extraction Method |

|--------|-----------|-------------------|

| PDF    | `.pdf`    | pypdf             |

| Text   | `.txt`    | Direct file read  |



Other file types are rejected with a clear error message.



### Chunking



Uploaded text is split into chunks with:



- **Chunk size:** 800 characters

- **Overlap:** 100 characters

- Empty chunks are removed; extra whitespace is normalized.



Chunks are stored in `backend/data/chunks.json` for future retrieval. Document metadata is stored in `backend/data/documents.json`.



### API Endpoints



| Method | Path            | Description                    |

|--------|-----------------|--------------------------------|

| GET    | `/`             | API status                     |

| GET    | `/health`       | Health check                   |

| POST   | `/kb/upload`    | Upload and process a document  |

| GET    | `/kb/documents` | List uploaded documents        |



Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)



#### POST `/kb/upload`



**Request:** `multipart/form-data` with a `file` field.



**Example success response:**

```json
{
  "status": "success",
  "message": "Document uploaded and processed successfully",
  "document": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "filename": "Project.pdf",
    "file_type": "pdf",
    "file_size": 245678,
    "file_size_readable": "240 KB",
    "chunks_created": 12,
    "uploaded_at": "30 Jun 2026, 02:25 PM",
    "status": "Processed"
  }
}
```

#### GET `/kb/documents`

**Example response:**

```json
{
  "documents": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "filename": "Project.pdf",
      "file_type": "pdf",
      "file_size": 245678,
      "file_size_readable": "240 KB",
      "chunks_created": 12,
      "uploaded_at": "30 Jun 2026, 02:25 PM",
      "status": "Processed"
    }
  ]
}
```

### Upload Workflow

1. User selects a PDF or TXT file on the Knowledge Base page.
2. Frontend sends `POST /kb/upload` with the file.
3. Backend validates type, saves to `uploads/`, extracts text, chunks content.
4. Metadata is written to `data/documents.json`; chunks to `data/chunks.json`.
5. Frontend shows a success toast and refreshes the document list.
6. Dashboard Recent Activity updates with the new upload.

### Metadata Structure

Each document in `backend/data/documents.json`:

| Field | Description |
|-------|-------------|
| `id` | UUID for the document |
| `filename` | Original file name |
| `file_type` | `pdf` or `txt` |
| `file_size` | Size in bytes |
| `file_size_readable` | Human-readable size (e.g. `240 KB`) |
| `chunks_created` | Number of text chunks |
| `uploaded_at` | Formatted timestamp (e.g. `30 Jun 2026, 02:25 PM`) |
| `status` | `Processed` on success |

Each chunk in `backend/data/chunks.json` includes `document_id`, `document_name`, `chunk_index`, `content`, and `created_at`.



### Current Limitations (Phase 2)



- No embeddings or vector search yet — these will be added in **Phase 3**.

- No ChromaDB integration yet.

- No chatbot or LLM answering.

- Metadata and chunks are stored in local JSON files (not a database).



---



## Run Commands Summary



| Service  | Directory  | Command                        | URL                      |

|----------|------------|--------------------------------|--------------------------|

| Frontend | `frontend` | `npm run dev`                  | http://localhost:3000    |

| Backend  | `backend`  | `uvicorn main:app --reload`    | http://127.0.0.1:8000    |



---



## Future Development Roadmap



### Phase 3 — Embeddings & Vector Search

- ChromaDB vector storage

- Embedding pipeline

- Semantic search over document chunks



### Phase 4 — MCP Tool Layer

- MCP server connections

- Tool registry and authentication

- Tool calling infrastructure



### Phase 5 — Agent & Decision Engine

- LLM provider integration (OpenAI, Gemini)

- Context assembly from knowledge + tools

- Agent orchestration and decision logic



### Phase 6 — Action Execution

- Email tool integration

- Task management tool integration

- End-to-end action workflows



---



## License



Private project — all rights reserved.

