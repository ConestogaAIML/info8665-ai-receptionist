from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import get_db
from app.schemas.appointment_prediction import (
    AtRiskListResponse,
    PredictionRequest,
    PredictionResponse,
)
from app.services.appointment_prediction_service import (
    check_appointment_conflict,
    get_appointment_recommendation,
    get_at_risk_appointments,
    get_available_slots,
    get_customer_history,
    get_customer_preferences,
    smart_book_appointment,
)

router = APIRouter(
    prefix="/api/appointments",
    tags=["Appointment Prediction"],
    dependencies=[Depends(verify_token)],
)


class SmartBookRequest(BaseModel):
    customer_id: int
    scheduled_at: Optional[str] = None
    duration_minutes: int = 30
    notes: Optional[str] = ""
    use_prediction: bool = True


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict no-show risk, recommend a slot, and store customer features",
)
def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    try:
        return get_appointment_recommendation(
            request.age,
            request.waiting_days,
            request.sms_received,
            db=db,
            client_id=request.client_id,
            client_name=request.client_name,
            save=request.save,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/customers/{customer_id}/history/")
def customer_history(customer_id: int):
    return get_customer_history(customer_id)


@router.get("/customers/{customer_id}/preferences/")
def customer_preferences(customer_id: int):
    return get_customer_preferences(customer_id)


@router.get("/availability/")
def availability(from_date: str, to_date: str, duration_minutes: int = 30):
    return get_available_slots(from_date, to_date, duration_minutes)


@router.get("/conflicts/check/")
def conflict_check(scheduled_at: str, duration_minutes: int = 30):
    return check_appointment_conflict(scheduled_at, duration_minutes)


@router.post("/smart-book/")
def smart_book(request: SmartBookRequest, db: Session = Depends(get_db)):
    from app.services.appointment_booking_rules import assert_client_rebookable

    # customer_id maps to client_id when booking against persisted clients
    assert_client_rebookable(db, request.customer_id)
    return smart_book_appointment(
        request.customer_id,
        request.scheduled_at,
        request.duration_minutes,
        request.notes or "",
        request.use_prediction,
    )


@router.get(
    "/at-risk/",
    response_model=AtRiskListResponse,
    summary="List high-risk customers from stored assessments",
)
def at_risk(db: Session = Depends(get_db)):
    return get_at_risk_appointments(db)
