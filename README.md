# AIVOA AI Complaint Copilot

AI-first customer complaint intake system for the pharmaceutical manufacturing
industry, built for the AIVOA Round 1 AI Product Engineer assignment. The AI
assistant owns the complaint data — the complaint form is never manually
filled; Redux is the single source of truth and is updated after AI
processing.

> **Status:** Feature-complete. The FastAPI backend, PostgreSQL persistence,
> LangGraph + Groq AI pipeline, and document text extraction (PDF/DOCX/TXT/
> EML) are all wired end-to-end — logging a complaint via chat or uploading a
> document runs the real AI workflow and populates the complaint form through
> Redux. Duplicate complaint detection is the one bonus feature left as a
> stub (`duplicateProbability` is always `0`).

## Tech Stack

**Frontend** — React (Vite + TypeScript), Redux Toolkit, React Router, Axios,
Tailwind CSS, Google Inter font.

**Backend** — Python, FastAPI, SQLAlchemy, PostgreSQL.

**AI** — LangGraph, Groq API (`gemma2-9b-it`).

## Project Structure

```
aivoa-ai-complaint-copilot/
├── client/                 # React + Vite + TypeScript frontend
│   └── src/
│       ├── components/     # layout/ and common/ reusable UI pieces
│       ├── features/       # feature-specific modules
│       ├── redux/          # store, hooks, slices
│       ├── services/       # Axios instance + API service modules
│       ├── hooks/          # custom React hooks
│       ├── pages/          # route-level pages
│       ├── types/          # shared TypeScript types
│       └── utils/          # helpers
├── server/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # routers (complaints, chat, documents) + deps.py (DI)
│   │   ├── database/       # SQLAlchemy engine/session (connection.py)
│   │   ├── models/         # ORM models (Complaint, ChatMessage, Document)
│   │   ├── schemas/        # Pydantic schemas (JSON-contract shaped, camelCase)
│   │   ├── services/       # business/service layer + Groq client
│   │   ├── langgraph/      # LangGraph state/nodes/workflow + LLM output parsing
│   │   ├── prompts/        # prompt templates for every AI node
│   │   └── utils/          # logging_config.py, exceptions.py, text_extraction.py
│   ├── migrations/          # Alembic migration scripts
│   ├── alembic.ini
│   └── main.py               # FastAPI app entrypoint
├── docs/                    # additional documentation
└── README.md
```

## Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL running locally (or a reachable instance)
- A Groq API key (for AI features — chat, document extraction, risk/summary/
  root-cause/CAPA generation)

## Frontend Setup (`client/`)

```bash
cd client
npm install
cp .env.example .env   # set VITE_API_BASE_URL if needed
npm run dev
```

The app runs at `http://localhost:5173`.


## Backend Setup (`server/`)

```bash
cd server
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # set DATABASE_URL and GROQ_API_KEY

# Create the database first if it doesn't exist yet, e.g.:
#   createdb aivoa_complaints
alembic upgrade head    # applies migrations/versions/*.py to your database

uvicorn main:app --reload --port 8000
```

The API runs at `http://localhost:8000`. Interactive docs are available at
`http://localhost:8000/docs`, and a health check is available at
`http://localhost:8000/health`.

Whenever the ORM models under `app/models/` change, generate a new
migration with `alembic revision --autogenerate -m "description"` and apply
it with `alembic upgrade head`.

## AI Workflow

Every chat message and document upload runs through the same LangGraph
pipeline (`app/langgraph/agent.py`):

```
Determine Workflow (source + existing complaint → intent, no LLM call)
        ↓
Extract Complaint Fields (Groq)
        ↓
Merge onto Current Complaint (pure logic — only changed fields overwrite)
        ↓
Assess Risk: severity / priority / risk level (Groq)
        ↓
Generate Summary (Groq)
        ↓
Recommend Root Cause (Groq)
        ↓
Recommend CAPA (Groq)
        ↓
Check Completeness (pure logic — required-field checklist)
        ↓
Validate & Assemble Final JSON Contract
```

Which branch (`log_complaint` / `edit_complaint` / `document_extraction`) runs
is decided by the calling endpoint and whether a complaint id resolved to an
existing row — never guessed by an LLM. All three branches converge on the
same extraction step; only the prompt built for that step changes (see
`app/prompts/complaint_prompts.py`).

Every Groq response is parsed and sanitized (`app/langgraph/parser.py`)
against a strict field/enum whitelist before it can be merged into state,
persisted, or returned — malformed or hallucinated fields are dropped rather
than trusted.

## Document Extraction

`POST /api/documents/upload` accepts a PDF, DOCX, TXT, or EML file, extracts
its plain text server-side (`app/utils/text_extraction.py` — `pypdf` for PDF,
`python-docx` for DOCX, Python's `email` module for EML), and feeds that text
through the same pipeline as chat (`source="document"`). One request goes
from raw file to a populated, persisted complaint. `POST /api/documents/extract`
remains available for running arbitrary pre-extracted text through the same
pipeline directly (useful for testing via `/docs`).

## API Overview

All routes are prefixed with `/api`. Full request/response schemas are
available interactively at `/docs`.

| Method | Path                     | Description                                                          |
| ------ | ------------------------ | --------------------------------------------------------------------- |
| POST   | `/complaints`             | Create a complaint                                                    |
| GET    | `/complaints`             | List complaints (paginated, filter by `status`/`severity`)            |
| GET    | `/complaints/{id}`        | Get one complaint, full AI JSON-contract shape                        |
| PATCH  | `/complaints/{id}`        | Update a complaint (core fields and/or AI-derived fields)              |
| GET    | `/chat/messages`          | List chat messages (optionally filter by `complaintId`)               |
| POST   | `/chat/messages`          | Send a message; runs the LangGraph/Groq pipeline and returns the reply |
| POST   | `/documents/upload`       | Upload a document; extracts text and runs it through the AI pipeline   |
| GET    | `/documents`               | List uploaded document metadata                                       |
| POST   | `/documents/extract`      | Run pre-extracted text through the AI pipeline directly                |
| GET    | `/health`                  | Health check (outside the `/api` prefix)                              |

Every error response (validation, 404s, unsupported file types, unhandled
exceptions) follows the same shape: `{ success, message, errors }`.

## Environment Variables

**`client/.env`**

| Variable            | Description               |
| ------------------- | -------------------------- |
| `VITE_API_BASE_URL` | Base URL of the FastAPI API |

**`server/.env`**

| Variable                     | Description                                     |
| ----------------------------- | ------------------------------------------------ |
| `ENVIRONMENT`                 | `development` / `production` (shown on `/health`) |
| `LOG_LEVEL`                   | Python logging level (`INFO`, `DEBUG`, ...)      |
| `DATABASE_URL`                | PostgreSQL connection string (SQLAlchemy URL)    |
| `GROQ_API_KEY`                | Groq API key                                     |
| `GROQ_MODEL`                  | Groq model name (`gemma2-9b-it`)                 |
| `CORS_ORIGINS`                | Comma-separated allowed origins                  |
| `DEFAULT_PAGE_SIZE`           | Default page size for list endpoints             |
| `MAX_PAGE_SIZE`                | Maximum allowed page size                        |
| `MAX_UPLOAD_SIZE_MB`          | Max accepted document upload size                |
| `ALLOWED_UPLOAD_EXTENSIONS`   | Comma-separated allowed document extensions      |

## Architecture

```
React → Redux Store → FastAPI → LangGraph → Groq LLM
     → Structured Complaint JSON → Redux updates UI → PostgreSQL Save
```

Every AI response follows a fixed JSON contract (`complaint`,
`riskAssessment`, `summary`, `completeness`, `rootCause`, `capa`,
`duplicateProbability`) — see `PROJECT_CONTEXT.md` for full details.

## Known Limitations

- **Duplicate complaint detection** is not implemented; `duplicateProbability`
  is always returned as `0`.
- Scanned/image-only PDFs (no embedded text layer) have no OCR fallback —
  `/documents/upload` returns a 422 if no text can be extracted.
