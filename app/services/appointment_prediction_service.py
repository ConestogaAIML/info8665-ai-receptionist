"""Appointment no-show prediction and risk assessment persistence."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from app.config import get_settings
from app.logging_config import configure_application_logging
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.risk_assessment import RiskAssessment

logger = configure_application_logging()
_model = None
booked_appointments = []

HIGH_RISK_THRESHOLD = 0.5
BUSINESS_HOURS = range(9, 17)


def _data_path() -> str:
    return get_settings().processed_data_path


def _model_path() -> Path:
    return Path(get_settings().model_path)


def load_appointments():
    return pd.read_csv(_data_path())


def _get_customer_data(customer_id: int):
    df = pd.read_csv(_data_path())

    if "PatientId" in df.columns:
        return df[df["PatientId"] == customer_id]

    return df[df["customer_id"] == customer_id]


def _get_model():
    global _model
    if _model is None:
        path = _model_path()
        logger.info(
            "Loading no-show model for experiment %s v%s from %s",
            get_settings().experiment_name,
            get_settings().experiment_version,
            path,
        )
        _model = joblib.load(path)
    return _model


def predict_no_show(age, waiting_days, weekday, hour, sms_received):
    prediction = _get_model().predict_proba(
        [[age, waiting_days, weekday, hour, sms_received]]
    )
    return prediction[0][1]


def recommendation_for_risk(risk: float) -> str:
    if risk < 0.3:
        return "Recommended"
    if risk <= 0.6:
        return "Medium Risk"
    return "High Risk"


def format_hour(hour: int) -> str:
    period = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    return f"{display_hour}:00 {period}"


def format_weekday(weekday: int) -> str:
    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    return weekdays[weekday]


def find_preferred_slot(age, waiting_days, sms_received):
    best_risk = float("inf")
    best_hour = 0
    best_weekday = 0

    for weekday in range(7):
        for hour in BUSINESS_HOURS:
            risk = predict_no_show(age, waiting_days, weekday, hour, sms_received)
            if risk < best_risk:
                best_risk = risk
                best_hour = hour
                best_weekday = weekday

    return best_hour, best_weekday, best_risk


def compute_profile_risk(age: int, waiting_days: int, sms_received: int) -> float:
    """Average no-show risk across business hours — used to flag high-risk customers."""
    risks = [
        predict_no_show(age, waiting_days, weekday, hour, sms_received)
        for weekday in range(7)
        for hour in BUSINESS_HOURS
    ]
    if not risks:
        return 0.0
    return float(sum(risks) / len(risks))


def get_appointment_recommendation(
    age: int,
    waiting_days: int,
    sms_received: int,
    *,
    db: Session | None = None,
    client_id: int | None = None,
    client_name: str | None = None,
    save: bool = True,
):
    settings = get_settings()
    logger.info(
        "Prediction request experiment=%s v%s features=%s client_id=%s save=%s",
        settings.experiment_name,
        settings.experiment_version,
        settings.feature_names,
        client_id,
        save,
    )

    preferred_hour, preferred_weekday, best_slot_risk = find_preferred_slot(
        age, waiting_days, sms_received
    )
    profile_risk = compute_profile_risk(age, waiting_days, sms_received)
    is_high_risk = profile_risk >= HIGH_RISK_THRESHOLD

    resolved_client_id = client_id
    is_new_customer = client_id is None
    resolved_name = (client_name or "").strip() or "New customer"

    if db is not None and client_id is not None:
        client = db.query(Client).filter(Client.id == client_id).first()
        if client is None:
            raise ValueError(f"Client {client_id} not found")
        resolved_name = f"{client.first_name} {client.last_name}".strip()
        prior = (
            db.query(RiskAssessment)
            .filter(RiskAssessment.client_id == client_id)
            .count()
        )
        is_new_customer = prior == 0
    elif db is not None and save and client_id is None and client_name:
        # Auto-create a lightweight client record for new customers so data persists.
        safe_slug = "".join(ch for ch in client_name.lower() if ch.isalnum())[:20] or "new"
        email = f"{safe_slug}.{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}@walkin.local"
        parts = client_name.strip().split(None, 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else "Customer"
        client = Client(
            first_name=first,
            last_name=last,
            email=email,
            phone="",
            notes="Created from AI Slot Advisor risk assessment",
        )
        db.add(client)
        db.flush()
        resolved_client_id = client.id
        resolved_name = f"{client.first_name} {client.last_name}".strip()
        is_new_customer = True

    assessment_id = None
    if db is not None and save:
        assessment = RiskAssessment(
            client_id=resolved_client_id,
            client_name=resolved_name,
            age=age,
            waiting_days=waiting_days,
            sms_received=sms_received,
            is_new_customer=is_new_customer,
            preferred_hour=format_hour(preferred_hour),
            preferred_weekday=format_weekday(preferred_weekday),
            best_slot_risk=float(round(best_slot_risk, 2)),
            profile_risk=float(round(profile_risk, 2)),
            recommendation=recommendation_for_risk(best_slot_risk),
            is_high_risk=is_high_risk,
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        assessment_id = assessment.id
        logger.info(
            "Saved risk assessment id=%s client_id=%s high_risk=%s profile_risk=%.2f",
            assessment_id,
            resolved_client_id,
            is_high_risk,
            profile_risk,
        )

    return {
        "preferred_hour": format_hour(preferred_hour),
        "preferred_weekday": format_weekday(preferred_weekday),
        "no_show_risk": float(round(best_slot_risk, 2)),
        "profile_risk": float(round(profile_risk, 2)),
        "recommendation": recommendation_for_risk(best_slot_risk),
        "is_high_risk": is_high_risk,
        "is_new_customer": is_new_customer,
        "client_id": resolved_client_id,
        "client_name": resolved_name,
        "assessment_id": assessment_id,
        "experiment_name": settings.experiment_name,
        "experiment_version": settings.experiment_version,
    }


def get_customer_history(customer_id: int):
    customer_data = _get_customer_data(customer_id)
    return {
        "customer_id": customer_id,
        "count": len(customer_data),
        "results": customer_data.head(10).to_dict(orient="records"),
    }


def get_customer_preferences(customer_id: int):
    customer_data = _get_customer_data(customer_id)

    if customer_data.empty:
        return {
            "customer_id": customer_id,
            "message": "No appointment history found",
        }

    preferred_hour = int(customer_data["AppointmentHour"].mode()[0])
    preferred_weekday = int(customer_data["AppointmentWeekday"].mode()[0])
    no_show_risk = float(customer_data["No-show"].mean())

    return {
        "customer_id": customer_id,
        "preferred_hour": preferred_hour,
        "preferred_weekday": preferred_weekday,
        "no_show_risk": round(no_show_risk, 2),
        "total_appointments": len(customer_data),
    }


def predict_appointments(customer_id: int, duration_minutes: int = 30):
    customer_data = _get_customer_data(customer_id)

    if customer_data.empty:
        slot_time = datetime.now().replace(
            hour=9, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        return {
            "customer_id": customer_id,
            "duration_minutes": duration_minutes,
            "suggestions": [
                {
                    "scheduled_at": slot_time.isoformat(),
                    "duration_minutes": duration_minutes,
                }
            ],
        }

    age = int(customer_data["Age"].iloc[0])
    sms_received = int(customer_data["SMS_received"].mode()[0])
    waiting_days = int(customer_data["WaitingDays"].median())

    preferred_hour, preferred_weekday, no_show_risk = find_preferred_slot(
        age, waiting_days, sms_received
    )

    now = datetime.now()
    days_ahead = (preferred_weekday - now.weekday()) % 7 or 7
    slot_time = (now + timedelta(days=days_ahead)).replace(
        hour=preferred_hour, minute=0, second=0, microsecond=0
    )

    return {
        "customer_id": customer_id,
        "duration_minutes": duration_minutes,
        "suggestions": [
            {
                "scheduled_at": slot_time.isoformat(),
                "duration_minutes": duration_minutes,
                "no_show_risk": float(round(no_show_risk, 2)),
            }
        ],
    }


def get_available_slots(from_date: str, to_date: str, duration_minutes: int = 30):
    start_date = datetime.fromisoformat(from_date)
    end_date = datetime.fromisoformat(to_date)

    slots = []
    current_date = start_date

    while current_date <= end_date:
        for hour in BUSINESS_HOURS:
            slot_time = current_date.replace(
                hour=hour, minute=0, second=0, microsecond=0
            )
            slots.append(
                {
                    "scheduled_at": slot_time.isoformat(),
                    "duration_minutes": duration_minutes,
                    "score": 80.0,
                    "reason": "Available conflict-free slot",
                    "conflict_free": True,
                }
            )
        current_date += timedelta(days=1)

    return {
        "from_date": from_date,
        "to_date": to_date,
        "duration_minutes": duration_minutes,
        "available_slots": slots,
        "total_slots": len(slots),
    }


def check_appointment_conflict(scheduled_at: str, duration_minutes: int = 30):
    for appointment in booked_appointments:
        if appointment["scheduled_at"] == scheduled_at:
            return {
                "scheduled_at": scheduled_at,
                "duration_minutes": duration_minutes,
                "has_conflict": True,
                "conflict_free": False,
                "message": "Slot already booked",
            }

    return {
        "scheduled_at": scheduled_at,
        "duration_minutes": duration_minutes,
        "has_conflict": False,
        "conflict_free": True,
        "message": "Slot is available",
    }


def smart_book_appointment(
    customer_id: int,
    scheduled_at: str | None,
    duration_minutes: int = 30,
    notes: str = "",
    use_prediction: bool = True,
):
    if use_prediction and not scheduled_at:
        prediction = predict_appointments(customer_id, duration_minutes)
        scheduled_at = prediction["suggestions"][0]["scheduled_at"]

    conflict = check_appointment_conflict(scheduled_at, duration_minutes)

    if conflict["has_conflict"]:
        return {
            "success": False,
            "message": "Cannot book appointment. Slot has conflict.",
        }

    appointment = {
        "id": len(booked_appointments) + 1,
        "customer_id": customer_id,
        "scheduled_at": scheduled_at,
        "duration_minutes": duration_minutes,
        "status": "scheduled",
        "notes": notes,
    }
    booked_appointments.append(appointment)

    return {
        "appointment": appointment,
        "booked_from_prediction": use_prediction,
        "message": "Appointment booked successfully",
    }


def record_no_show_risk(db: Session, client_id: int) -> RiskAssessment:
    """When a manager marks a skipped appointment, flag that client as high risk."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if client is None:
        raise ValueError(f"Client {client_id} not found")

    client_name = f"{client.first_name} {client.last_name}".strip()
    prior = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.client_id == client_id)
        .order_by(RiskAssessment.created_at.desc())
        .first()
    )

    assessment = RiskAssessment(
        client_id=client_id,
        client_name=client_name,
        age=prior.age if prior else 0,
        waiting_days=prior.waiting_days if prior else 0,
        sms_received=prior.sms_received if prior else 0,
        is_new_customer=False,
        preferred_hour=prior.preferred_hour if prior else "",
        preferred_weekday=prior.preferred_weekday if prior else "",
        best_slot_risk=1.0,
        profile_risk=1.0,
        recommendation="High Risk",
        is_high_risk=True,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    logger.info(
        "Recorded no-show risk assessment id=%s client_id=%s name=%s",
        assessment.id,
        client_id,
        client_name,
    )
    return assessment


def get_at_risk_appointments(db: Session):
    """High-risk from ML assessments plus anyone with a skipped (no_show) appointment."""
    from sqlalchemy.orm import joinedload

    from app.services.appointment_booking_rules import rebook_eligible_at

    def _skip_reason(client_id: int | None) -> str:
        if client_id is None:
            return "Skipped appointment"
        eligible = rebook_eligible_at(db, client_id)
        if eligible is None:
            return "Skipped appointment"
        now = datetime.now(timezone.utc)
        if now < eligible:
            return (
                f"Skipped appointment — rebooking blocked until {eligible.date().isoformat()}"
            )
        return "Skipped appointment"

    assessments = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.is_high_risk.is_(True))
        .order_by(RiskAssessment.created_at.desc())
        .all()
    )

    seen: set[str] = set()
    results = []

    for item in assessments:
        key = (
            f"client:{item.client_id}"
            if item.client_id is not None
            else f"name:{item.client_name}:{item.id}"
        )
        if item.client_id is not None and key in seen:
            continue
        if item.client_id is not None:
            seen.add(key)

        is_skip = item.profile_risk >= 1.0 and item.recommendation == "High Risk"
        eligible = (
            rebook_eligible_at(db, item.client_id)
            if item.client_id is not None
            else None
        )
        in_cooldown = eligible is not None and datetime.now(timezone.utc) < eligible
        if in_cooldown:
            reason = _skip_reason(item.client_id)
        elif is_skip:
            reason = "Skipped appointment"
        else:
            reason = "Predicted high risk"
        results.append(
            {
                "assessment_id": item.id,
                "customer_id": item.client_id,
                "client_name": item.client_name,
                "no_show_risk": item.best_slot_risk,
                "profile_risk": item.profile_risk,
                "is_new_customer": item.is_new_customer,
                "requires_confirmation": True,
                "age": item.age,
                "waiting_days": item.waiting_days,
                "sms_received": item.sms_received,
                "reason": reason,
            }
        )

    # Include clients with recorded no-shows even if assessment insert was missed.
    skipped = (
        db.query(Appointment)
        .options(joinedload(Appointment.client))
        .filter(Appointment.status == "no_show")
        .order_by(Appointment.updated_at.desc())
        .all()
    )
    for appt in skipped:
        key = f"client:{appt.client_id}"
        if key in seen:
            continue
        seen.add(key)
        name = f"{appt.client.first_name} {appt.client.last_name}".strip()
        results.insert(
            0,
            {
                "assessment_id": 0,
                "customer_id": appt.client_id,
                "client_name": name,
                "no_show_risk": 1.0,
                "profile_risk": 1.0,
                "is_new_customer": False,
                "requires_confirmation": True,
                "age": 0,
                "waiting_days": 0,
                "sms_received": 0,
                "reason": _skip_reason(appt.client_id),
            },
        )

    return {"count": len(results), "results": results}
