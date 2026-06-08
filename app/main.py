from fastapi import FastAPI
from app.database import Base, engine
from app.models import Visitor  # noqa: F401 — registers model with Base
from app.routers import receptionist

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Receptionist",
    description="INFO8665 — AI Receptionist API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(receptionist.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "AI Receptionist is running. Visit /docs for the API."}
