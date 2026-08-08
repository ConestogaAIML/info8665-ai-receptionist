from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    age: int = Field(ge=0, description="Patient age")
    waiting_days: int = Field(ge=0, description="Days between scheduling and appointment")
    sms_received: int = Field(ge=0, le=1, description="Whether an SMS reminder was sent (0 or 1)")
    client_id: int | None = Field(
        default=None,
        description="Existing client ID. Omit for a new / walk-in customer.",
    )
    client_name: str | None = Field(
        default=None,
        description="Display name when creating/assessing a new customer.",
    )
    save: bool = Field(
        default=True,
        description="Persist features + prediction to the database for at-risk tracking.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "age": 62,
                    "waiting_days": 5,
                    "sms_received": 0,
                    "client_name": "Alex New",
                    "save": True,
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    preferred_hour: str
    preferred_weekday: str
    no_show_risk: float
    profile_risk: float
    recommendation: str
    is_high_risk: bool
    is_new_customer: bool
    client_id: int | None = None
    client_name: str | None = None
    assessment_id: int | None = None
    experiment_name: str | None = None
    experiment_version: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "preferred_hour": "10:00 AM",
                    "preferred_weekday": "Tuesday",
                    "no_show_risk": 0.06,
                    "profile_risk": 0.42,
                    "recommendation": "Recommended",
                    "is_high_risk": False,
                    "is_new_customer": True,
                    "client_name": "Alex New",
                    "experiment_name": "appointment-no-show",
                    "experiment_version": "1.0.0",
                }
            ]
        }
    }


class AtRiskClient(BaseModel):
    assessment_id: int
    customer_id: int | None
    client_name: str
    no_show_risk: float
    profile_risk: float
    is_new_customer: bool
    requires_confirmation: bool
    age: int
    waiting_days: int
    sms_received: int
    reason: str | None = None


class AtRiskListResponse(BaseModel):
    count: int
    results: list[AtRiskClient]
