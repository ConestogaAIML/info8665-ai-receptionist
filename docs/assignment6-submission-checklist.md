# Assignment 6 Submission Checklist — AI Receptionist

Use this checklist when assembling the **one-page PDF** for the dropbox.

## Required on the PDF

- [ ] Project name: **AI Receptionist**
- [ ] Screenshot: app running locally (UI http://localhost:3000)
- [ ] Screenshot: API docs http://localhost:8000/docs (show ML Ops Pipelines section)
- [ ] Screenshot: Docker Secrets / public config (`/config/public` or Streamlit :8501)
- [ ] Docker Hub URL: `https://hub.docker.com/r/<DOCKERHUB_USER>/ai-receptionist`
- [ ] Azure DevOps project link
- [ ] GitHub repo link: `https://github.com/ConestogaAIML/info8665-ai-receptionist`
- [ ] Pull request link (to instructor)
- [ ] Any Azure Boards Sprint 6 / UAT task links

## Project management (Azure Boards)

- [ ] End Sprint 5; start Sprint 6
- [ ] Move unfinished Sprint 5 work → Sprint 6 with discussion comment + @mentions
- [ ] Assign instructor a User Acceptance Testing task
- [ ] Merge feature branch → `main`
- [ ] Create new branch for next sprint (e.g. `sprint-7/...`)
- [ ] Open PR and request instructor review

## Local Docker verify

```bash
cp .env.example .env
docker compose up --build
```

- UI: http://localhost:3000  
- API: http://localhost:8000/docs  
- Streamlit logs/secrets: http://localhost:8501  

## Publish image

```bash
docker build -t <DOCKERHUB_USER>/ai-receptionist:latest .
docker login
docker push <DOCKERHUB_USER>/ai-receptionist:latest
```

## Quick ML Ops smoke test (after JWT)

1. `POST /api/ml/faq/collect` → `preprocess` → `train` → `validate` → `reload`
2. `POST /api/ml/appointments/run-full`
3. `POST /api/appointments/predict`
4. `POST /api/businesses/1/chat/`
