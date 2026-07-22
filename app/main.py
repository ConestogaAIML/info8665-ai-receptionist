from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.config import get_settings
from app.database import Base, engine, ensure_schema
from app.logging_config import configure_application_logging, get_log_file_path, read_recent_log_lines
from app.models import Business, BusinessFAQ, Service, Client, Appointment  # noqa: F401 — registers tables
from app.routers import (
    appointment_prediction,
    appointments,
    auth,
    businesses,
    chat,
    clients,
    dev_seed,
    faq,
    services,
)

ensure_schema()
logger = configure_application_logging()
settings = get_settings()
logger.info("AI Receptionist application logging initialized")
logger.info(
    "Secrets management active: experiment=%s version=%s db_engine=%s host=%s",
    settings.experiment_name,
    settings.experiment_version,
    settings.db_engine,
    settings.db_hostname,
)
logger.info(
    "ML secrets loaded: features=%s epochs=%s n_estimators=%s expected_accuracy=%.3f",
    settings.feature_names,
    settings.ml_epochs,
    settings.ml_n_estimators,
    settings.expected_accuracy,
)

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
app.include_router(dev_seed.router)
app.include_router(appointment_prediction.router)
app.include_router(appointments.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "Call POST /auth/token, copy the access_token value, "
                "click Authorize above, and paste it here."
            ),
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", tags=["Root"])
def root():
    logger.info("Root status endpoint requested")
    return {"message": "AI Receptionist is running. Visit /docs for the API."}


@app.get("/config/public", tags=["Secrets Management"])
def public_config():
    """Expose non-secret configuration for DevOps verification (no passwords)."""
    logger.info("Public config endpoint requested")
    return get_settings().safe_summary()


@app.get("/logs/recent", tags=["Log Management"])
def recent_logs(limit: int = 50):
    logger.info("Recent log entries requested")
    return {
        "log_file": str(get_log_file_path()),
        "lines": read_recent_log_lines(limit=limit),
    }
