from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.database import Base, engine
from app.models import Business, BusinessFAQ, Service, Client, Appointment  # noqa: F401 — registers tables
from app.routers import (
    # appointment_prediction,
    # appointments,
    auth,
    businesses,
    chat,
    clients,
    faq,
    services,
)

Base.metadata.create_all(bind=engine)

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
# app.include_router(appointments.router)
# app.include_router(appointment_prediction.router)


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
    return {"message": "AI Receptionist is running. Visit /docs for the API."}
