# AI Receptionist — SOA Service Contracts (Assignment 6)
# Updated from A5 design for ML Ops pipelines

**Project:** AI Receptionist  
**Course:** INFO8665  
**Group:** AI Receptionist Scrum Team  
**Version:** 6.0 (Sprint 6 / Assignment 6)

This document updates the A5 SOA Service Contract with **at least six service contracts per ML use case**. Each ML Ops pipeline stage is encapsulated as an authenticated API service.

**Auth:** JWT Bearer from `POST /auth/token`  
**Base URL (local):** `http://localhost:8000`  
**OpenAPI:** `/docs`

---

## ML Use Case 1 — FAQ Intent Chatbot

Pipeline stages: Data Collection → EDA → Preprocess → Train → Validate → Serve/Reload → Integration (chat)

| # | Contract | Method / Path | Parameters | Response (key fields) | Pipeline stage |
|---|----------|---------------|------------|------------------------|----------------|
| 1 | Collect FAQ training data | `POST /api/ml/faq/collect` | Body: `source` (`local` \| `db`) | `dataset_path`, `row_count`, `status` | Data collection |
| 2 | FAQ EDA | `GET /api/ml/faq/eda` | Query: `csv_path?` | `row_count`, `unique_labels`, `label_distribution`, `avg_text_length` | EDA |
| 3 | FAQ preprocess | `POST /api/ml/faq/preprocess` | Body: `csv_path?` | `rows_before`, `rows_after`, `output_path` | Preprocessing |
| 4 | Train FAQ classifier | `POST /api/ml/faq/train` | Body: `csv_path?` | `accuracy`, `train_samples`, `test_samples`, `model_path`, `classes` | Training |
| 5 | Validate FAQ model | `POST /api/ml/faq/validate` | Body: `csv_path?` | `accuracy`, `expected_accuracy`, `met_expectation` | Validation |
| 6 | Reload FAQ serving cache | `POST /api/ml/faq/reload` | — | `loaded`, `model_path`, `status` | Model serving |
| 7 | Chat integration (serve) | `POST /api/businesses/{business_id}/chat/` | Path: `business_id`; Body: `message` | `answer`, `category`, `confidence`, `fallback` | Integration |

### FAQ contract details

#### SC-FAQ-01 Collect
- **Purpose:** Assemble offline/custom FAQ training CSV (Docker-safe; optional DB merge).
- **Errors:** `400` missing dataset; `401` unauthorized.

#### SC-FAQ-02 EDA
- **Purpose:** Summarize label distribution and text length stats.

#### SC-FAQ-03 Preprocess
- **Purpose:** Normalize text/labels, drop empties/duplicates, write combined CSV.

#### SC-FAQ-04 Train
- **Purpose:** Fit TF-IDF + LogisticRegression; persist `training/faq_classifier.joblib`.

#### SC-FAQ-05 Validate
- **Purpose:** Holdout accuracy vs expected threshold (0.70).

#### SC-FAQ-06 Reload
- **Purpose:** Clear in-process model cache so serving uses the latest artifact.

#### SC-FAQ-07 Chat (integration)
- **Purpose:** Classify user utterance and return business FAQ answer.

---

## ML Use Case 2 — Appointment No-Show Prediction

Pipeline stages: Preprocess/EDA → Train → Validate → Reload → Predict (serve) → Smart-book / At-risk (integration)

| # | Contract | Method / Path | Parameters | Response (key fields) | Pipeline stage |
|---|----------|---------------|------------|------------------------|----------------|
| 1 | Appointment preprocess | `POST /api/ml/appointments/preprocess` | Body: `raw_path?` | `processed_path`, `status` | Preprocessing / data prep |
| 2 | Appointment EDA | `GET /api/ml/appointments/eda` | — | `feature_names`, `processed_rows`, `target_rate`, secrets experiment metadata | EDA |
| 3 | Train no-show model | `POST /api/ml/appointments/train` | — (hyperparams from secrets) | `accuracy`, `expected_accuracy`, `met_expectation`, `model_path` | Training |
| 4 | Validate no-show model | `POST /api/ml/appointments/validate` | — | `accuracy`, `expected_accuracy`, `met_expectation` | Validation |
| 5 | Reload no-show model | `POST /api/ml/appointments/reload` | — | `exists`, `model_path`, `status` | Model serving |
| 6 | Predict / slot advisor | `POST /api/appointments/predict` | Body: `age`, `waiting_days`, `sms_received`, `client_id?`, `client_name?`, `save` | `no_show_risk`, `profile_risk`, `preferred_hour`, `preferred_weekday`, `recommendation` | Model serving |
| 7 | Full pipeline | `POST /api/ml/appointments/run-full` | Body: `raw_path?` | nested `train` + `validate` results | Integration orchestration |
| 8 | At-risk integration | `GET /api/appointments/at-risk/` | — | `count`, `results[]` with risk + skip cooldown reason | Integration |
| 9 | Smart-book integration | `POST /api/appointments/smart-book/` | Body: `customer_id`, `scheduled_at?`, … | booked appointment / conflict message | Integration |

### Appointment contract details

#### SC-NS-01 Preprocess
- **Purpose:** Feature engineering from raw appointments using secret `FEATURE_NAMES`.

#### SC-NS-02 EDA
- **Purpose:** Report dataset readiness and target no-show rate.

#### SC-NS-03 Train
- **Purpose:** Train RandomForest with secrets-managed hyperparameters; save `MODEL_PATH`.

#### SC-NS-04 Validate
- **Purpose:** Compare accuracy to `EXPECTED_ACCURACY` secret.

#### SC-NS-05 Reload
- **Purpose:** Drop cached model so next `/predict` loads new weights.

#### SC-NS-06 Predict
- **Purpose:** Score no-show risk and recommend low-risk slot.

#### SC-NS-07 Run-full
- **Purpose:** Execute preprocess → train → validate in one API call (ML Ops orchestration).

#### SC-NS-08 / SC-NS-09 Integration
- **Purpose:** Surface high-risk clients and automated booking using the served model.

---

## Cross-cutting operational contracts

| Contract | Path | Notes |
|----------|------|-------|
| App health | `GET /` | Confirms API process is running |
| Public secrets summary | `GET /config/public` | Non-secret DevOps verification (no passwords) |
| Recent logs | `GET /logs/recent` | Pipeline/API log inspection UI companion |
| Auth token | `POST /auth/token` | Issues JWT for all ML pipeline calls |

---

## Logging policy (A6 / A8 / A9)

- Application start: logged in `app/main.py`
- Each pipeline stage: `START` / `END` (and failure) in service modules
- Each service-contract API: `API START` / `API END` at router entry

---

## Mapping to MLOps_UseCase_API_Design (Week 5)

| Week-5 stage | FAQ contracts | Appointment contracts |
|--------------|---------------|------------------------|
| Data collection | SC-FAQ-01 | SC-NS-01 (raw → processed) |
| EDA | SC-FAQ-02 | SC-NS-02 |
| Preprocessing | SC-FAQ-03 | SC-NS-01 |
| Training | SC-FAQ-04 | SC-NS-03 |
| Validation | SC-FAQ-05 | SC-NS-04 |
| Model serving | SC-FAQ-06, SC-FAQ-07 | SC-NS-05, SC-NS-06 |
| Integration | SC-FAQ-07 | SC-NS-07, SC-NS-08, SC-NS-09 |
