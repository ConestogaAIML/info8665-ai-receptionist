from datetime import datetime
from pydantic import BaseModel, field_validator


class BusinessFAQCreate(BaseModel):
    question: str
    answer: str
    category: str = ""
    tags: list[str] = []
    is_active: bool = True

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What are your business hours?",
                    "answer": "We are open Monday to Friday, 9 AM to 6 PM, and Saturday 10 AM to 4 PM.",
                    "category": "hours",
                    "tags": ["hours", "general"],
                    "is_active": True,
                }
            ]
        }
    }


class BusinessFAQUpdate(BaseModel):
    question: str
    answer: str
    category: str = ""
    tags: list[str] = []
    is_active: bool = True


class BusinessFAQResponse(BaseModel):
    id: int
    business_id: int
    question: str
    answer: str
    category: str
    tags: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("tags", mode="before")
    @classmethod
    def split_tags(cls, v):
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        return v


class BusinessFAQListResponse(BaseModel):
    count: int
    results: list[BusinessFAQResponse]
