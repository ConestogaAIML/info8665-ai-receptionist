from datetime import datetime
from pydantic import BaseModel, EmailStr


class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str = ""
    notes: str = ""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "email": "jane.doe@example.com",
                    "phone": "555-0100",
                    "notes": "Prefers afternoon appointments.",
                }
            ]
        }
    }


class ClientUpdate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str = ""
    notes: str = ""


class ClientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClientListResponse(BaseModel):
    count: int
    results: list[ClientResponse]
