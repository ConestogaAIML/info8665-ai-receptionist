from datetime import datetime
from pydantic import BaseModel, field_validator


class FAQCreate(BaseModel):
    question: str
    answer: str
    tags: list[str] = []
    is_active: bool = True

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What are your business hours?",
                    "answer": "We are open Monday to Friday, 9 AM to 5 PM.",
                    "tags": ["hours", "general"],
                    "is_active": True,
                }
            ]
        }
    }


class FAQUpdate(BaseModel):
    question: str
    answer: str
    tags: list[str] = []
    is_active: bool = True


class FAQResponse(BaseModel):
    id: int
    question: str
    answer: str
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


class FAQListResponse(BaseModel):
    count: int
    results: list[FAQResponse]
