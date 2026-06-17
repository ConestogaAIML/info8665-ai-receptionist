from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"message": "What are your business hours?"},
            ]
        }
    }


class ChatResponse(BaseModel):
    answer: str
    matched_question: str | None = None
    category: str | None = None
    confidence: float
    fallback: bool
