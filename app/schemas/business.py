from datetime import datetime
from pydantic import BaseModel


class BusinessCreate(BaseModel):
    name: str
    description: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    business_hours: str = ""
    website: str = ""
    is_active: bool = True

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Bella Hair Studio",
                    "description": "A full-service hair salon specializing in cuts, color, and styling.",
                    "phone": "519-555-0101",
                    "email": "info@bellahairstudio.com",
                    "address": "123 Main St, Waterloo, ON N2L 3G1",
                    "business_hours": "Mon-Fri 9am-6pm, Sat 10am-4pm",
                    "website": "https://bellahairstudio.com",
                    "is_active": True,
                }
            ]
        }
    }


class BusinessUpdate(BaseModel):
    name: str
    description: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    business_hours: str = ""
    website: str = ""
    is_active: bool = True


class BusinessResponse(BaseModel):
    id: int
    name: str
    description: str
    phone: str
    email: str
    address: str
    business_hours: str
    website: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BusinessListResponse(BaseModel):
    count: int
    results: list[BusinessResponse]
