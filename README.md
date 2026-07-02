# KnowledgeHub AI – Production-Ready Personal Knowledge Assistant (RAG)

KnowledgeHub AI is a highly performant, personal knowledge management assistant powered by Retrieval-Augmented Generation (RAG). Users can upload documents of various formats (PDF, DOCX, TXT, Markdown, GitHub URL, YouTube transcript, manual notes), search them semantically, and ask natural language questions. The application is built with elite software engineering practices: a React + TypeScript frontend, a FastAPI (clean architecture) backend, a PostgreSQL relational database, and Qdrant vector search.

---

## Key Features

1. **Authentication & User Management**:
   - Secure signup and login flow.
   - Dual-token structure (JWT Access Token + Refresh Token Rotation with `jti` invalidation).
   - Password hashing using the memory-hard **Argon2id** algorithm (`argon2-cffi`).
   - Role-based route control (`user` and `admin`).

2. **Multi-Source Ingestion Pipeline**:
   - **PDF Parsing**: Page-level extraction using PyMuPDF (`pymupdf`).
   - **DOCX Parsing**: Paragraph and block extraction using `python-docx`.
   - **Plain Text / MD**: Clean text normalization.
   - **GitHub Repositories**: Clones repositories, ignores binaries/config, and indexes relevant code.
   - **YouTube Video Transcripts**: Automatic fetch of transcripts via `youtube-transcript-api`.
   - **Manual Notes**: Native Rich Text Note editor powered by TipTap.

3. **Asynchronous Vector Processing**:
   - Text cleaning and splitting using LangChain's `RecursiveCharacterTextSplitter` configured for token-based chunking (~512 tokens).
   - Local embedding generation utilizing HuggingFace's **BAAI/bge-small-en-v1.5** model (384-dimensions, normalized).
   - Parallel insert and payload indexing (`user_id`, `source_type`, `document_id`) in Qdrant vector database.

4. **Inference with Proper Citations**:
   - Asks questions and streams tokens via Server-Sent Events (SSE).
   - Context injection with custom prompt engineering boundaries to prevent hallucinations.
   - Outputs strict source citations (file name, page number, chunk ID).

5. **Dashboards & Audit Logs**:
   - User statistics (Document counts, query totals, storage used, API speeds).
   - Admin panels to control registration logs, active queues, and system alerts.

---

## System Architecture

```
                    ┌──────────────────────────────┐
                    │  React TypeScript Frontend   │
                    │   Vite + Tailwind v4 + Query  │
                    └──────────────┬───────────────┘
                                   │ HTTPS / SSE
                                   ▼
                    ┌──────────────────────────────┐
                    │    FastAPI Python Backend    │
                    │   Clean Layered Architecture  │
                    └──────────────┬───────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼ (SQLAlchemy)            ▼ (gRPC/REST)             ▼ (HTTP)
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│    PostgreSQL    │      │  Qdrant Vector   │      │Google Gemini API │
│ Relational DB    │      │    Database      │      │gemini-2.0-flash  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

---

## Tech Stack & Versions

### Frontend
- **Framework**: React 19 + TypeScript + Vite 5/6
- **Styling**: Tailwind CSS v4 (using `@tailwindcss/vite`)
- **HTTP Client**: Axios with JWT auto-refresh interceptors
- **State & Fetching**: TanStack React Query v5
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI `0.138.0` + Uvicorn
- **ORM & Migrations**: SQLAlchemy `2.0.51` (Async) + Alembic `1.18.5`
- **Vector DB Client**: `qdrant-client` `1.18.0`
- **Embedding Model**: `sentence-transformers` `5.6.0` (BAAI/bge-small-en-v1.5, local inference)
- **Gemini SDK**: `google-genai` (Official SDK)
- **Auth**: `PyJWT[crypto]` + `argon2-cffi`
- **File Utilities**: `pymupdf` `1.28.0`, `python-docx` `1.2.0`, `youtube-transcript-api`

---

## Getting Started

### Prerequisites
- Install **Docker** & **Docker Desktop**.
- Install **Node.js** (v20+ or v22).
- Install **Python 3.12**.

### 1. Environment Configuration
Create a `.env` file in the root directory by copying the template:
```bash
cp .env.example .env
```
Open the `.env` file and insert your API keys (e.g., Google Gemini API key).

### 2. Multi-Container Orchestration (Docker Compose)
Start the PostgreSQL, Qdrant, backend, and frontend containers:
```bash
docker compose -f docker/docker-compose.yml up --build -d
```
The services will be available at:
- **Frontend App**: `http://localhost:3000`
- **Backend Swagger UI**: `http://localhost:8000/docs`
- **Qdrant Dashboard**: `http://localhost:6333/dashboard`

### 3. Local Development Setup (Manual)

#### Backend Setup
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## Verification & Testing

### Automated Tests
Run backend tests to verify database, authentication, and pipeline configurations:
```bash
cd backend
python -m pytest tests/ -v
```

### System Health
Verify backend connection check:
```bash
curl http://localhost:8000/api/v1/health
```
Expected output:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "components": {
      "database": "healthy",
      "qdrant": "healthy",
      "embedding_model": "loaded_on_first_use"
    }
  }
}
```
