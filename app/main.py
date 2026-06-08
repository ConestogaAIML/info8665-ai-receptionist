from fastapi import FastAPI
from app.routers import receptionist

app = FastAPI(
    title="AI Receptionist",
    description="INFO8665 — AI Receptionist API",
    version="0.1.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

app.include_router(receptionist.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "AI Receptionist is running. Visit /docs for the API."}
