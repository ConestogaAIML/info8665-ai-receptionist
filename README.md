# INFO8665 — AI Receptionist

A FastAPI-based AI receptionist service with SQLite persistence, JWT authentication, Swagger UI, and Docker Compose support.

---

## Project Structure

```
info8665-ai-receptionist/
├── README.md
├── orchestrator.ipynb        # Pipeline orchestrator: load data → train → run
├── requirements.txt          # Pinned Python dependencies
├── Dockerfile                # Container image definition
├── docker-compose.yml        # Docker Compose with persistent SQLite volume
├── .env.example              # Environment variable reference
│
├── app/                      # FastAPI application
│   ├── main.py               # App entry point, Swagger at /docs
│   ├── database.py           # SQLAlchemy engine & session
│   ├── auth.py               # JWT creation and verification
│   ├── models/
│   │   └── faq.py            # FAQ ORM model
│   ├── routers/
│   │   ├── auth.py           # POST /auth/token — dev token issuer
│   │   └── faq.py            # FAQ Knowledge Base CRUD routes
│   └── schemas/
│       └── faq.py            # Pydantic request/response schemas
│
├── data-collection/          # Raw datasets and database source files
├── training/                 # Trained model artifacts
│   └── trained-model-v0.h5
├── dev/
│   └── dev-run-v0.py         # Execution script (called by orchestrator)
└── documentation/            # Project documentation
    ├── api-contract.md       # Human-readable API design contract
    └── openapi.json          # Machine-generated OpenAPI 3.1.0 spec
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker Desktop (for containerised run)

### Local Development

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API (hot-reload enabled)
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`.  
Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

### Docker Compose

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up --build -d

# Stop and remove containers
docker compose down
```

The SQLite database is stored in a named Docker volume (`sqlite-data`) and persists across restarts.

---

## Authentication

All `/api/*` endpoints require a **Bearer JWT** token.

**Step 1 — Get a token**

```bash
curl -X POST "http://localhost:8000/auth/token?business_id=1"
```

```json
{ "access_token": "<token>", "token_type": "bearer" }
```

**Step 2 — Use the token**

```bash
curl http://localhost:8000/api/faq/ \
  -H "Authorization: Bearer <token>"
```

> In Swagger UI: call `POST /auth/token`, copy the token, click **Authorize**, and paste it.

---

## API Endpoints

### Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/token` | — | Issue a dev JWT token |

### FAQ Knowledge Base

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/faq/` | JWT | List all FAQ items (filter by `tags`, `is_active`) |
| `POST` | `/api/faq/` | JWT | Create a new FAQ item |
| `GET` | `/api/faq/{id}/` | JWT | Get a single FAQ item |
| `PUT` | `/api/faq/{id}/` | JWT | Full update of a FAQ item |
| `DELETE` | `/api/faq/{id}/` | JWT | Delete a FAQ item |

### Root

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/` | — | Service status |

### Example — Create a FAQ

```bash
curl -X POST http://localhost:8000/api/faq/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are your business hours?",
    "answer": "We are open Monday to Friday, 9 AM to 5 PM.",
    "tags": ["hours", "general"],
    "is_active": true
  }'
```

```json
{
  "id": 1,
  "question": "What are your business hours?",
  "answer": "We are open Monday to Friday, 9 AM to 5 PM.",
  "tags": ["hours", "general"],
  "is_active": true,
  "created_at": "2026-06-08T22:08:28.860490",
  "updated_at": "2026-06-08T22:08:28.860493"
}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SQLITE_DB_PATH` | `./data/receptionist.db` | Path to the SQLite database file |
| `JWT_SECRET_KEY` | `dev-secret-change-in-production` | Secret key for signing JWT tokens |

Copy `.env.example` to `.env` to customise locally.

---

## Pipeline (Orchestrator)

`orchestrator.ipynb` drives the full ML pipeline:

1. **Load data** — reads datasets from `data-collection/`
2. **Train & save** — outputs model artifacts to `training/trained-model-v0.h5`
3. **Execute** — calls `dev/dev-run-v0.py` to start the API server

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-06-08 | FAQ Knowledge Base CRUD, JWT auth, Docker Compose, SQLite |
