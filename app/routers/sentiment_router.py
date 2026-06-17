from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import get_db
from app.models.sentiment_model import SentimentLog
from app.schemas.sentiment_schemas import (
    CategoryBreakdown,
    CategoryValue,
    EscalationItem,
    EscalationListResponse,
    SentimentAnalyzeRequest,
    SentimentAnalyzeResponse,
    SentimentBatchRequest,
    SentimentBatchResponse,
    SentimentBatchItem,
    SentimentDeleteResponse,
    SentimentLogCreate,
    SentimentLogListResponse,
    SentimentLogResponse,
    SentimentLogUpdate,
    SentimentSummaryResponse,
    SentimentBreakdown,
    SentimentValue,
)
from app.services.sentiment_service import analyze

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment Analysis"])


# ─── POST /analyze ────────────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=SentimentAnalyzeResponse,
    summary="Analyze sentiment of a conversation",
    description=(
        "Runs TF-IDF + Logistic Regression inference on the provided conversation text. "
        "Returns the detected sentiment (positive/neutral/negative), emotion label, "
        "intent category (making_appointment, cancel_appointment, ask_question, other), "
        "confidence score, and an escalation flag when the customer appears frustrated."
    ),
)
def analyze_sentiment(
    payload: SentimentAnalyzeRequest,
    _: dict = Depends(verify_token),
):
    result = analyze(payload.text)
    return SentimentAnalyzeResponse(
        conversation_id=payload.conversation_id,
        text=payload.text,
        sentiment=result.sentiment,
        emotion=result.emotion,
        category=result.category,
        confidence=result.confidence,
        escalate=result.escalate,
        analyzed_at=result.analyzed_at,
    )


# ─── POST /analyze/batch ──────────────────────────────────────────────────────

@router.post(
    "/analyze/batch",
    response_model=SentimentBatchResponse,
    summary="Batch-analyze multiple conversations",
    description="Analyze up to 50 conversation texts in a single request.",
)
def analyze_batch(
    payload: SentimentBatchRequest,
    _: dict = Depends(verify_token),
):
    results = []
    for item in payload.conversations:
        r = analyze(item.text)
        results.append(
            SentimentBatchItem(
                conversation_id=item.conversation_id,
                sentiment=r.sentiment,
                emotion=r.emotion,
                category=r.category,
                confidence=r.confidence,
                escalate=r.escalate,
            )
        )
    return SentimentBatchResponse(processed=len(results), results=results)


# ─── POST /log ────────────────────────────────────────────────────────────────

@router.post(
    "/log",
    response_model=SentimentLogResponse,
    status_code=201,
    summary="Persist a sentiment analysis result",
    description=(
        "Saves a completed sentiment analysis result to the database. "
        "Use this after calling /analyze to create an auditable record and "
        "supply labelled data for future ML retraining via DVC."
    ),
)
def log_sentiment(
    payload: SentimentLogCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    entry = SentimentLog(
        conversation_id=payload.conversation_id,
        text=payload.text,
        sentiment=payload.sentiment,
        emotion=payload.emotion,
        category=payload.category,
        confidence=payload.confidence,
        escalate=payload.escalate,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# ─── GET /log/{conversation_id} ───────────────────────────────────────────────

@router.get(
    "/log/{conversation_id}",
    response_model=SentimentLogResponse,
    summary="Get sentiment log for a conversation",
)
def get_log(
    conversation_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    entry = (
        db.query(SentimentLog)
        .filter(SentimentLog.conversation_id == conversation_id)
        .order_by(SentimentLog.logged_at.desc())
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Sentiment log not found")
    return entry


# ─── GET /logs ────────────────────────────────────────────────────────────────

@router.get(
    "/logs",
    response_model=SentimentLogListResponse,
    summary="List all sentiment logs with optional filters",
)
def list_logs(
    sentiment: Optional[SentimentValue] = Query(default=None, description="Filter by sentiment"),
    category: Optional[CategoryValue] = Query(default=None, description="Filter by intent category"),
    escalate: Optional[bool] = Query(default=None, description="Filter by escalation flag"),
    from_date: Optional[datetime] = Query(default=None, description="Start date filter (ISO8601)"),
    to_date: Optional[datetime] = Query(default=None, description="End date filter (ISO8601)"),
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    q = db.query(SentimentLog)
    if sentiment is not None:
        q = q.filter(SentimentLog.sentiment == sentiment)
    if category is not None:
        q = q.filter(SentimentLog.category == category)
    if escalate is not None:
        q = q.filter(SentimentLog.escalate == escalate)
    if from_date is not None:
        q = q.filter(SentimentLog.logged_at >= from_date)
    if to_date is not None:
        q = q.filter(SentimentLog.logged_at <= to_date)
    items = q.order_by(SentimentLog.logged_at.desc()).all()
    return SentimentLogListResponse(count=len(items), results=items)


# ─── GET /escalations ─────────────────────────────────────────────────────────

@router.get(
    "/escalations",
    response_model=EscalationListResponse,
    summary="Get all conversations flagged for human escalation",
)
def list_escalations(
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    q = db.query(SentimentLog).filter(SentimentLog.escalate == True)  # noqa: E712
    if from_date:
        q = q.filter(SentimentLog.logged_at >= from_date)
    if to_date:
        q = q.filter(SentimentLog.logged_at <= to_date)
    items = q.order_by(SentimentLog.logged_at.desc()).all()
    results = [
        EscalationItem(
            conversation_id=e.conversation_id,
            sentiment=e.sentiment,
            emotion=e.emotion,
            category=e.category,
            escalated_at=e.logged_at,
        )
        for e in items
    ]
    return EscalationListResponse(count=len(results), results=results)


# ─── GET /summary ─────────────────────────────────────────────────────────────

@router.get(
    "/summary",
    response_model=SentimentSummaryResponse,
    summary="Get aggregated sentiment statistics for dashboard reporting",
)
def sentiment_summary(
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    q = db.query(SentimentLog)
    if from_date:
        q = q.filter(SentimentLog.logged_at >= from_date)
    if to_date:
        q = q.filter(SentimentLog.logged_at <= to_date)
    all_items = q.all()
    total = len(all_items)

    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    category_counts = {"making_appointment": 0, "cancel_appointment": 0, "ask_question": 0, "other": 0}
    escalated = 0

    for item in all_items:
        sentiment_counts[item.sentiment] = sentiment_counts.get(item.sentiment, 0) + 1
        category_counts[item.category] = category_counts.get(item.category, 0) + 1
        if item.escalate:
            escalated += 1

    return SentimentSummaryResponse(
        total_analyzed=total,
        sentiment_breakdown=SentimentBreakdown(**sentiment_counts),
        category_breakdown=CategoryBreakdown(**category_counts),
        escalation_rate=round(escalated / total, 4) if total else 0.0,
    )


# ─── PUT /log/{log_id} ────────────────────────────────────────────────────────

@router.put(
    "/log/{log_id}",
    response_model=SentimentLogResponse,
    summary="Correct a sentiment log entry (human-in-the-loop feedback)",
    description=(
        "Allows a human reviewer to override an ML prediction. "
        "Corrections are flagged in the DB and fed back into the DVC retraining pipeline."
    ),
)
def update_log(
    log_id: int,
    payload: SentimentLogUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    entry = db.query(SentimentLog).filter(SentimentLog.id == log_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Sentiment log not found")
    entry.sentiment = payload.sentiment
    entry.emotion = payload.emotion
    entry.category = payload.category
    entry.escalate = payload.escalate
    entry.corrected = True
    entry.correction_note = payload.correction_note
    entry.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(entry)
    return entry


# ─── DELETE /log/{log_id} ─────────────────────────────────────────────────────

@router.delete(
    "/log/{log_id}",
    status_code=204,
    summary="Delete a specific sentiment log entry",
    description="Removes a single log entry for GDPR / data-subject deletion requests.",
)
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    entry = db.query(SentimentLog).filter(SentimentLog.id == log_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Sentiment log not found")
    db.delete(entry)
    db.commit()


# ─── DELETE /logs/purge ───────────────────────────────────────────────────────

@router.delete(
    "/logs/purge",
    response_model=SentimentDeleteResponse,
    summary="Bulk-delete logs older than a given date (data retention policy)",
)
def purge_logs(
    before_date: datetime = Query(..., description="Delete all logs with logged_at before this ISO8601 datetime"),
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    entries = db.query(SentimentLog).filter(SentimentLog.logged_at < before_date).all()
    count = len(entries)
    for e in entries:
        db.delete(e)
    db.commit()
    return SentimentDeleteResponse(
        deleted_count=count,
        message=f"Purged {count} log entries before {before_date.isoformat()}",
    )
