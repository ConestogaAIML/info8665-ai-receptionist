from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    age: int = Field(ge=0, description="Patient age")
    waiting_days: int = Field(ge=0, description="Days between scheduling and appointment")
    sms_received: int = Field(ge=0, le=1, description="Whether an SMS reminder was sent (0 or 1)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "age": 62,
                    "waiting_days": 5,
                    "sms_received": 0,
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    preferred_hour: str
    preferred_weekday: str
    no_show_risk: float
    recommendation: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "preferred_hour": "10:00 AM",
                    "preferred_weekday": "Tuesday",
                    "no_show_risk": 0.06,
                    "recommendation": "Recommended",
                }
            ]
        }
    }
