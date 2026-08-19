# INFO8665 — AI Receptionist

A FastAPI-based AI receptionist service with a TF-IDF FAQ chatbot, Next.js chat UI, SQLite persistence, JWT authentication, Swagger UI, and Docker Compose support.

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
│   │   ├── faq.py            # FAQ Knowledge Base CRUD routes
│   │   └── chat.py           # POST /api/businesses/{id}/chat/ — FAQ chatbot
│   ├── schemas/
│   │   ├── faq.py            # Pydantic request/response schemas
│   │   └── chat.py           # ChatRequest / ChatResponse schemas
│   └── services/
│       └── faq_classifier.py # TF-IDF inference service
│
├── frontend/                 # Next.js 16 chat UI (shadcn/ui)
│   ├── src/
│   │   ├── app/              # App Router (layout, page)
│   │   ├── components/chat/  # ChatPage, BusinessSelector, MessageBubble, etc.
│   │   ├── hooks/            # useBusinesses, useChat
│   │   └── lib/api/          # auth, client, businesses, chat fetch helpers
│   ├── .env.local            # NEXT_PUBLIC_API_URL=http://localhost:8000
│   └── package.json
│
├── data-collection/          # Raw datasets and database source files
│   └── faq_training_data.csv # Labeled FAQ intent training data (86 examples, 6 categories)
├── training/                 # Trained model artifacts
│   ├── train_faq_classifier.py
│   └── faq_classifier.joblib
├── docs/
│   └── research-faq-chatbot-classifier.md
├── dev/
│   ├── dev-run-v0.py         # Execution script (called by orchestrator)
│   └── seed.py               # Seed sample businesses and FAQs
└── documentation/            # Project documentation
    ├── api-contract.md       # Human-readable API design contract
    └── openapi.json          # Machine-generated OpenAPI 3.1.0 spec
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop (for containerised run)

### Sync the latest team changes

Use this before running the project so your local folder matches the team branch:

```bash
git fetch --all --prune
git switch feat/assignment6-mlops-pipelines
git pull --ff-only
```

To update local `main` as well:

```bash
git fetch origin main:main
```

### Run the backend

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

### Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`, click **Connect**, select a business, and start chatting.

### Secrets Management (Docker environment variables)

Sensitive and experiment settings are loaded from environment variables (see `.env.example`). Copy and edit before running:

```bash
cp .env.example .env
```

| Category | Variables |
|----------|-----------|
| Database | `DB_USERNAME`, `DB_PASSWORD`, `DB_HOSTNAME`, `DB_PORT`, `DB_NAME`, `DB_ENGINE` |
| Auth | `JWT_SECRET_KEY` |
| EDA features | `FEATURE_NAMES`, `TARGET_COLUMN` |
| Training | `ML_N_ESTIMATORS`, `ML_MAX_DEPTH`, `ML_EPOCHS`, `ML_TEST_SIZE`, `ML_RANDOM_STATE` |
| Experiment | `EXPERIMENT_NAME`, `EXPERIMENT_VERSION`, `EXPECTED_ACCURACY` |

Non-secret settings are visible at `GET /config/public` (passwords are never exposed).

### Docker Compose (full stack)

Run the API, Streamlit log GUI, and Next.js frontend together:

```bash
# Build and start all services
cp .env.example .env   # if you have not already
docker compose up --build
```

| Service | URL |
|---------|-----|
| Next.js chat UI | `http://localhost:3000` |
| FastAPI + Swagger | `http://localhost:8000/docs` |
| Streamlit log GUI | `http://localhost:8501` |
| Public config (secrets summary) | `http://localhost:8000/config/public` |

**Run in the background**

```bash
docker compose up --build -d
docker compose logs -f          # stream logs
```

On startup the API container automatically seeds sample businesses, FAQs, clients, services, and one appointment.

The SQLite database is stored in a named Docker volume (`sqlite-data`) and persists across restarts.

### Run tests

After installing Python dependencies locally:

```bash
python -m pytest -q
```

After building the Docker image:

```bash
docker compose exec api python -m pytest -q
```

The Docker image includes the `tests/` directory, so the same test command works inside the running container.

### Publish to Docker Hub

```bash
docker build -t <dockerhub-username>/ai-receptionist:latest .
docker run --rm -p 8000:8000 -p 8501:8501 -p 3000:3000 --env-file .env <dockerhub-username>/ai-receptionist:latest
docker push <dockerhub-username>/ai-receptionist:latest
```

### Assignment 4: Log Management GUI

The Docker `api` service starts both FastAPI and the Streamlit GUI in one container:

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | `dev-secret-change-in-production` | Secret for signing JWT tokens |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend URL the browser calls |
| `SQLITE_DB_PATH` | `/data/receptionist.db` | SQLite file path inside the container |

Override at build or runtime:

```bash
NEXT_PUBLIC_API_URL=https://api.example.com docker compose up --build
```

**Push to Docker Hub**

Add an `image:` tag to each service in `docker-compose.yml`, then:

```bash
docker login
docker compose build
docker compose push
```

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

### FAQ Chatbot

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/businesses/{business_id}/chat/` | JWT | Ask the FAQ chatbot a question |

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

### Example — Ask the FAQ chatbot

```bash
curl -X POST http://localhost:8000/api/businesses/1/chat/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your business hours?"}'
```

```json
{
  "answer": "We are open Monday to Friday, 9 AM to 6 PM, and Saturday 10 AM to 4 PM.",
  "matched_question": "What are your business hours?",
  "category": "hours",
  "confidence": 0.87,
  "fallback": false
}
```

---

| Variable | Default | Description |
|----------|---------|-------------|
| `SQLITE_DB_PATH` | `./data/receptionist.db` | Path to the SQLite database file |
| `JWT_SECRET_KEY` | `dev-secret-change-in-production` | Secret key for signing JWT tokens |
| `FAQ_MODEL_PATH` | `./training/faq_classifier.joblib` | Path to the trained FAQ classifier model |

Copy `.env.example` to `.env` to customise locally.

---

## Pipeline (Orchestrator)

`orchestrator.ipynb` drives the full ML pipeline:

1. **Load data** — reads `data-collection/faq_training_data.csv`
2. **Train & save** — trains a TF-IDF + LogisticRegression classifier and saves to `training/faq_classifier.joblib`
3. **Execute** — calls `dev/dev-run-v0.py` to start the API server

You can also train the model directly:

```bash
python training/train_faq_classifier.py
```

Export external datasets to local CSV (avoids repeated Hugging Face downloads):

```bash
pip install fsspec huggingface_hub

# Download Bitext, remap labels, save to data-collection/bitext_mapped.csv
python training/export_dataset.py bitext

# Merge custom + Bitext into data-collection/faq_training_combined.csv
python training/export_dataset.py merge

# Train on the combined dataset
python training/train_faq_classifier.py data-collection/faq_training_combined.csv
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.6.0 | 2026-08-08 | Assignment 6: ML Ops pipeline APIs, SOA contracts, Docker ML assets |
| 0.2.0 | 2026-06-15 | Next.js chat UI with shadcn/ui, auth gate, business selector, confidence/category metadata |
| 0.1.1 | 2026-06-15 | TF-IDF FAQ chatbot classifier and `/chat/` endpoint |
| 0.1.0 | 2026-06-08 | FAQ Knowledge Base CRUD, JWT auth, Docker Compose, SQLite |

---

## Assignment 6 — CI/CD and ML Ops Pipelines

### ML Ops pipeline APIs (JWT required)

Both ML use cases expose pipeline stages as HTTP services (see `docs/soa-service-contracts.md`).

**FAQ chatbot**

| Stage | Endpoint |
|-------|----------|
| Collect | `POST /api/ml/faq/collect` |
| EDA | `GET /api/ml/faq/eda` |
| Preprocess | `POST /api/ml/faq/preprocess` |
| Train | `POST /api/ml/faq/train` |
| Validate | `POST /api/ml/faq/validate` |
| Reload | `POST /api/ml/faq/reload` |
| Serve | `POST /api/businesses/{id}/chat/` |

**Appointment no-show**

| Stage | Endpoint |
|-------|----------|
| Preprocess | `POST /api/ml/appointments/preprocess` |
| EDA | `GET /api/ml/appointments/eda` |
| Train | `POST /api/ml/appointments/train` |
| Validate | `POST /api/ml/appointments/validate` |
| Reload | `POST /api/ml/appointments/reload` |
| Full pipeline | `POST /api/ml/appointments/run-full` |
| Serve | `POST /api/appointments/predict` |

### Docker (full stack)

```bash
cp .env.example .env
docker compose up --build
```

- UI: http://localhost:3000  
- API / Swagger: http://localhost:8000/docs  
- Streamlit logs & secrets: http://localhost:8501  

### Publish to Docker Hub

```bash
docker build -t <DOCKERHUB_USER>/ai-receptionist:latest .
docker login
docker push <DOCKERHUB_USER>/ai-receptionist:latest
```

### Documentation

- SOA contracts: [`docs/soa-service-contracts.md`](docs/soa-service-contracts.md)
- Submission checklist: [`docs/assignment6-submission-checklist.md`](docs/assignment6-submission-checklist.md)
