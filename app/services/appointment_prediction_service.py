import joblib
import pandas as pd
from datetime import datetime, timedelta

model = joblib.load(
    "data/model/no_show_model.pkl"
)

DATA_PATH = "data/processed/processed_appointments.csv"

booked_appointments = []


def load_appointments():
    return pd.read_csv(DATA_PATH)


def _get_customer_data(customer_id: int):
    df = pd.read_csv(DATA_PATH)

    if "PatientId" in df.columns:
        return df[df["PatientId"] == customer_id]

    return df[df["customer_id"] == customer_id]


def predict_no_show(
    age,
    waiting_days,
    weekday,
    hour,
    sms_received
):
    prediction = model.predict_proba([
        [
            age,
            waiting_days,
            weekday,
            hour,
            sms_received
        ]
    ])

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
        for hour in range(24):
            risk = predict_no_show(
                age,
                waiting_days,
                weekday,
                hour,
                sms_received,
            )
            if risk < best_risk:
                best_risk = risk
                best_hour = hour
                best_weekday = weekday

    return best_hour, best_weekday, best_risk


def get_appointment_recommendation(age, waiting_days, sms_received):
    preferred_hour, preferred_weekday, no_show_risk = find_preferred_slot(
        age,
        waiting_days,
        sms_received,
    )

    return {
        "preferred_hour": format_hour(preferred_hour),
        "preferred_weekday": format_weekday(preferred_weekday),
        "no_show_risk": float(round(no_show_risk, 2)),
        "recommendation": recommendation_for_risk(no_show_risk),
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
        age,
        waiting_days,
        sms_received,
    )

    now = datetime.now()
    days_ahead = (preferred_weekday - now.weekday()) % 7 or 7
    slot_time = (now + timedelta(days=days_ahead)).replace(
        hour=preferred_hour,
        minute=0,
        second=0,
        microsecond=0,
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
        for hour in range(9, 17):
            slot_time = current_date.replace(
                hour=hour, minute=0, second=0, microsecond=0
            )

            slots.append({
                "scheduled_at": slot_time.isoformat(),
                "duration_minutes": duration_minutes,
                "score": 80.0,
                "reason": "Available conflict-free slot",
                "conflict_free": True,
            })

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


def get_at_risk_appointments():
    df = load_appointments()

    at_risk = []

    customer_ids = (
        df["PatientId"].unique()
        if "PatientId" in df.columns
        else df["customer_id"].unique()
    )

    for customer_id in customer_ids[:20]:
        preference = get_customer_preferences(int(customer_id))

        if "no_show_risk" in preference and preference["no_show_risk"] >= 0.5:
            at_risk.append({
                "customer_id": int(customer_id),
                "no_show_risk": preference["no_show_risk"],
                "requires_confirmation": True,
            })

    return {
        "count": len(at_risk),
        "results": at_risk,
    }
