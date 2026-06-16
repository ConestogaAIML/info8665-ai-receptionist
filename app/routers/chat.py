from difflib import SequenceMatcher

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import get_db
from app.models.business import Business
from app.models.faq import BusinessFAQ
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import faq_classifier

router = APIRouter(
    prefix="/api/businesses/{business_id}/chat",
    tags=["FAQ Chatbot"],
)

CONFIDENCE_THRESHOLD = 0.40
FALLBACK_MESSAGE = (
    "I'm not sure about that. Please contact us directly for more help."
)


def _get_business_or_404(business_id: int, db: Session) -> Business:
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


def _best_matching_faq(message: str, faqs: list[BusinessFAQ]) -> BusinessFAQ:
    return max(
        faqs,
        key=lambda faq: SequenceMatcher(None, message.lower(), faq.question.lower()).ratio(),
    )


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Ask the FAQ chatbot a question",
)
def chat(
    business_id: int,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    _get_business_or_404(business_id, db)
    category, confidence = faq_classifier.predict(payload.message)
    print(f"Category: {category}, Confidence: {confidence}")
    if category is None or confidence < CONFIDENCE_THRESHOLD:
        return ChatResponse(
            answer=FALLBACK_MESSAGE,
            matched_question=None,
            category=category,
            confidence=confidence,
            fallback=True,
        )

    faqs = (
        db.query(BusinessFAQ)
        .filter(
            BusinessFAQ.business_id == business_id,
            BusinessFAQ.category == category,
            BusinessFAQ.is_active == True,  # noqa: E712
        )
        .all()
    )

    if not faqs:
        return ChatResponse(
            answer=FALLBACK_MESSAGE,
            matched_question=None,
            category=category,
            confidence=confidence,
            fallback=True,
        )

    best_faq = _best_matching_faq(payload.message, faqs)
    return ChatResponse(
        answer=best_faq.answer,
        matched_question=best_faq.question,
        category=category,
        confidence=confidence,
        fallback=False,
    )
