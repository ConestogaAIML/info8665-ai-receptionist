from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


SentimentValue = Literal["positive", "neutral", "negative"]
CategoryValue = Literal["making_appointment", "cancel_appointment", "ask_question", "other"]


# ─── Request schemas ───────────────────────────────────────────────────────────

class SentimentAnalyzeRequest(BaseModel):
    conversation_id: str = Field(..., description="Unique ID of the conversation")
    text: str = Field(..., min_length=1, description="Raw conversation text to analyze")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "conversation_id": "conv_001",
                    "text": "I am really frustrated — you double-booked my appointment again and I want it cancelled immediately.",
                }
            ]
        }
    }


class SentimentBatchRequest(BaseModel):
    conversations: list[SentimentAnalyzeRequest] = Field(
        ..., min_length=1, max_length=50, description="List of conversations to analyze"
    )


class SentimentLogCreate(BaseModel):
    conversation_id: str
    sentiment: SentimentValue
    emotion: Optional[str] = None
    category: CategoryValue
    confidence: float = Field(..., ge=0.0, le=1.0)
    escalate: bool = False
    text: Optional[str] = None


class SentimentLogUpdate(BaseModel):
    sentiment: SentimentValue
    emotion: Optional[str] = None
    category: CategoryValue
    escalate: bool
    correction_note: Optional[str] = None


# ─── Response schemas ──────────────────────────────────────────────────────────

class SentimentAnalyzeResponse(BaseModel):
    conversation_id: str
    text: str
    sentiment: SentimentValue
    emotion: Optional[str]
    category: CategoryValue
    confidence: float
    escalate: bool
    analyzed_at: datetime


class SentimentBatchItem(BaseModel):
    conversation_id: str
    sentiment: SentimentValue
    emotion: Optional[str]
    category: CategoryValue
    confidence: float
    escalate: bool


class SentimentBatchResponse(BaseModel):
    processed: int
    results: list[SentimentBatchItem]


class SentimentLogResponse(BaseModel):
    id: int
    conversation_id: str
    text: Optional[str]
    sentiment: SentimentValue
    emotion: Optional[str]
    category: CategoryValue
    confidence: float
    escalate: bool
    corrected: bool
    correction_note: Optional[str]
    logged_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SentimentLogListResponse(BaseModel):
    count: int
    results: list[SentimentLogResponse]


class EscalationItem(BaseModel):
    conversation_id: str
    sentiment: SentimentValue
    emotion: Optional[str]
    category: CategoryValue
    escalated_at: datetime

    model_config = {"from_attributes": True}


class EscalationListResponse(BaseModel):
    count: int
    results: list[EscalationItem]


class SentimentBreakdown(BaseModel):
    positive: int
    neutral: int
    negative: int


class CategoryBreakdown(BaseModel):
    making_appointment: int
    cancel_appointment: int
    ask_question: int
    other: int


class SentimentSummaryResponse(BaseModel):
    total_analyzed: int
    sentiment_breakdown: SentimentBreakdown
    category_breakdown: CategoryBreakdown
    escalation_rate: float


class SentimentDeleteResponse(BaseModel):
    deleted_count: int
    message: str
