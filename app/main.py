from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models import Business, BusinessFAQ, Service, Client, Appointment  # noqa: F401 — registers tables
from app.routers import auth, faq, services, clients, appointments
from app.routers import businesses, chat
from app.routers import sentiment_router  # ← sentiment router added

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
app.include_router(sentiment_router.router)  # ← sentiment added

@app.get("/", tags=["Root"])
def root():
    return {"message": "AI Receptionist is running. Visit /docs for the API."}
