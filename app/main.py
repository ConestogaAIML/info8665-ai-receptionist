from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.database import Base, engine
from app.logging_config import configure_application_logging, get_log_file_path, read_recent_log_lines
from app.models import Business, BusinessFAQ, Service, Client, Appointment  # noqa: F401 — registers tables
from app.routers import auth, faq, services, clients, appointments
from app.routers import businesses, chat

Base.metadata.create_all(bind=engine)
logger = configure_application_logging()
logger.info("AI Receptionist application logging initialized")

app = FastAPI(
    title="AI Receptionist",
    description=(
        "INFO8665 — AI Receptionist API\n\n"
        "**Authentication:** Use `POST /auth/token` to get a JWT, "
        "then click **Authorize** and paste the `access_token` value."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.state.logger = logger

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(businesses.router)
app.include_router(faq.router)
app.include_router(chat.router)
app.include_router(services.router)
app.include_router(clients.router)
app.include_router(appointments.router)


@app.get("/", tags=["Root"])
def root():
    logger.info("Root status endpoint requested")
    return {"message": "AI Receptionist is running. Visit /docs for the API."}


@app.get("/logs/recent", tags=["Log Management"])
def recent_logs(limit: int = 50):
    logger.info("Recent log entries requested")
    return {
        "log_file": str(get_log_file_path()),
        "lines": read_recent_log_lines(limit=limit),
    }
