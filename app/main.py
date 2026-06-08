from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.database import Base, engine
from app.models import Visitor, FAQ  # noqa: F401 — registers models with Base
from app.routers import receptionist, faq, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Receptionist",
    description=(
        "INFO8665 — AI Receptionist API\n\n"
        "**Authentication:** Use `POST /auth/token` to get a JWT, "
        "then click **Authorize** and paste it."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(auth.router)
app.include_router(receptionist.router)
app.include_router(faq.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "AI Receptionist is running. Visit /docs for the API."}
