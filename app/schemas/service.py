from datetime import datetime
from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    description: str = ""
    duration_minutes: int
    price: float
    category: str = ""
    is_active: bool = True

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Classic Haircut",
                    "description": "Wash, cut, and style.",
                    "duration_minutes": 45,
                    "price": 35.00,
                    "category": "Hair",
                    "is_active": True,
                }
            ]
        }
    }


class ServiceUpdate(BaseModel):
    name: str
    description: str = ""
    duration_minutes: int
    price: float
    category: str = ""
    is_active: bool = True


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str
    duration_minutes: int
    price: float
    category: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceListResponse(BaseModel):
    count: int
    results: list[ServiceResponse]
