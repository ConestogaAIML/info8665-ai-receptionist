from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import verify_token
from app.schemas.appointment_prediction import PredictionRequest, PredictionResponse
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
    summary="Predict no-show risk and recommend a slot",
)
def predict(request: PredictionRequest):
    return get_appointment_recommendation(
        request.age,
        request.waiting_days,
        request.sms_received,
    )


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
def smart_book(request: SmartBookRequest):
    return smart_book_appointment(
        request.customer_id,
        request.scheduled_at,
        request.duration_minutes,
        request.notes or "",
        request.use_prediction,
    )


@router.get("/at-risk/")
def at_risk():
    return get_at_risk_appointments()
