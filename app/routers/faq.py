import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import get_db
from app.logging_config import LOGGER_NAME
from app.models.business import Business
from app.models.faq import BusinessFAQ
from app.schemas.faq import (
    BusinessFAQCreate,
    BusinessFAQListResponse,
    BusinessFAQResponse,
    BusinessFAQUpdate,
)

router = APIRouter(
    prefix="/api/businesses/{business_id}/faqs",
    tags=["Business FAQs"],
)
logger = logging.getLogger(LOGGER_NAME)


def _get_business_or_404(business_id: int, db: Session) -> Business:
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


def _tags_to_str(tags: list[str]) -> str:
    return ",".join(t.strip() for t in tags)


@router.get(
    "/",
    response_model=BusinessFAQListResponse,
    summary="List all FAQs for a business",
)
def list_faqs(
    business_id: int,
    category: str | None = Query(default=None, description="Filter by category"),
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    _get_business_or_404(business_id, db)
    q = db.query(BusinessFAQ).filter(BusinessFAQ.business_id == business_id)
    if category is not None:
        q = q.filter(BusinessFAQ.category == category)
    if is_active is not None:
        q = q.filter(BusinessFAQ.is_active == is_active)
    items = q.order_by(BusinessFAQ.created_at.desc()).all()
    logger.info("FAQ list requested for business_id=%s with count=%s", business_id, len(items))
    return BusinessFAQListResponse(count=len(items), results=items)


@router.post(
    "/",
    response_model=BusinessFAQResponse,
    status_code=201,
    summary="Create a FAQ for a business",
)
def create_faq(
    business_id: int,
    payload: BusinessFAQCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    _get_business_or_404(business_id, db)
    faq = BusinessFAQ(
        business_id=business_id,
        question=payload.question,
        answer=payload.answer,
        category=payload.category,
        tags=_tags_to_str(payload.tags),
        is_active=payload.is_active,
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    logger.info("FAQ item created with id=%s for business_id=%s", faq.id, business_id)
    return faq


@router.get(
    "/{faq_id}/",
    response_model=BusinessFAQResponse,
    summary="Get a FAQ for a business",
)
def get_faq(
    business_id: int,
    faq_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    _get_business_or_404(business_id, db)
    faq = (
        db.query(BusinessFAQ)
        .filter(BusinessFAQ.id == faq_id, BusinessFAQ.business_id == business_id)
        .first()
    )
    if not faq:
        logger.info("FAQ item lookup missed for business_id=%s id=%s", business_id, faq_id)
        raise HTTPException(status_code=404, detail="FAQ not found")
    logger.info("FAQ item retrieved with id=%s for business_id=%s", faq_id, business_id)
    return faq


@router.put(
    "/{faq_id}/",
    response_model=BusinessFAQResponse,
    summary="Full update of a FAQ for a business",
)
def update_faq(
    business_id: int,
    faq_id: int,
    payload: BusinessFAQUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    _get_business_or_404(business_id, db)
    faq = (
        db.query(BusinessFAQ)
        .filter(BusinessFAQ.id == faq_id, BusinessFAQ.business_id == business_id)
        .first()
    )
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    faq.question = payload.question
    faq.answer = payload.answer
    faq.category = payload.category
    faq.tags = _tags_to_str(payload.tags)
    faq.is_active = payload.is_active
    db.commit()
    db.refresh(faq)
    logger.info("FAQ item updated with id=%s for business_id=%s", faq_id, business_id)
    return faq


@router.delete("/{faq_id}/", status_code=204, summary="Delete a FAQ for a business")
def delete_faq(
    business_id: int,
    faq_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    _get_business_or_404(business_id, db)
    faq = (
        db.query(BusinessFAQ)
        .filter(BusinessFAQ.id == faq_id, BusinessFAQ.business_id == business_id)
        .first()
    )
    if not faq:
        logger.info("FAQ item delete missed for business_id=%s id=%s", business_id, faq_id)
        raise HTTPException(status_code=404, detail="FAQ not found")
    db.delete(faq)
    db.commit()
    logger.info("FAQ item deleted with id=%s for business_id=%s", faq_id, business_id)
