from datetime import datetime
from pydantic import BaseModel, field_validator

VALID_STATUSES = {"scheduled", "completed", "cancelled"}


class AppointmentCreate(BaseModel):
    client_id: int
    service_id: int
    appointment_date: str   # "YYYY-MM-DD"
    appointment_time: str   # "HH:MM"
    status: str = "scheduled"
    notes: str = ""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "client_id": 1,
                    "service_id": 1,
                    "appointment_date": "2026-07-15",
                    "appointment_time": "10:00",
                    "status": "scheduled",
                    "notes": "",
                }
            ]
        }
    }

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        return v


class AppointmentUpdate(BaseModel):
    client_id: int
    service_id: int
    appointment_date: str
    appointment_time: str
    status: str = "scheduled"
    notes: str = ""

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        return v


class AppointmentResponse(BaseModel):
    id: int
    client_id: int
    service_id: int
    client_name: str
    service_name: str
    appointment_date: str
    appointment_time: str
    status: str
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppointmentListResponse(BaseModel):
    count: int
    results: list[AppointmentResponse]
