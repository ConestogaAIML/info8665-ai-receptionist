# INFO8665 — AI Receptionist

A FastAPI-based AI receptionist service with SQLite persistence, Swagger UI, and Docker Compose support.

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
│   ├── models/
│   │   └── visitor.py        # Visitor ORM model
│   ├── routers/
│   │   └── receptionist.py   # API routes (CRUD)
│   └── schemas/
│       └── receptionist.py   # Pydantic request/response schemas
│
├── data-collection/          # Raw datasets and database source files
├── training/                 # Trained model artifacts
│   └── trained-model-v0.h5
├── dev/
│   └── dev-run-v0.py         # Execution script (called by orchestrator)
└── documentation/            # Project documentation
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

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root — service status |
| `GET` | `/receptionist/health` | Health check |
| `POST` | `/receptionist/greet` | Check in a visitor |
| `GET` | `/receptionist/visitors` | List all visitors |
| `GET` | `/receptionist/visitors/{id}` | Get a visitor by ID |
| `DELETE` | `/receptionist/visitors/{id}` | Check out a visitor |

### Example Request

```bash
curl -X POST http://localhost:8000/receptionist/greet \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "purpose": "Job interview", "host": "Alice Smith"}'
```

```json
{
  "id": 1,
  "name": "Jane Doe",
  "purpose": "Job interview",
  "host": "Alice Smith",
  "status": "checked-in",
  "created_at": "2026-06-08T21:55:33.813287"
}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SQLITE_DB_PATH` | `./data/receptionist.db` | Path to the SQLite database file |

Copy `.env.example` to `.env` to customise locally.

---

## Pipeline (Orchestrator)

`orchestrator.ipynb` drives the full ML pipeline:

1. **Load data** — reads datasets from `data-collection/`
2. **Train & save** — outputs model artifacts to `training/trained-model-v0.h5`
3. **Execute** — calls `dev/dev-run-v0.py` to start the API server
