from fastapi import APIRouter
from app.schemas.receptionist import VisitorRequest, VisitorResponse

router = APIRouter(prefix="/receptionist", tags=["Receptionist"])


@router.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@router.post("/greet", response_model=VisitorResponse, summary="Greet a visitor")
def greet_visitor(payload: VisitorRequest):
    host_part = f" to see {payload.host}" if payload.host else ""
    message = f"Welcome, {payload.name}! You are here for: {payload.purpose}{host_part}."
    return VisitorResponse(message=message, visitor=payload.name, status="checked-in")
