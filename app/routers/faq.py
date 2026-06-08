from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth import verify_token
from app.database import get_db
from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQListResponse, FAQResponse, FAQUpdate

router = APIRouter(prefix="/api/faq", tags=["FAQ Knowledge Base"])


def _tags_to_str(tags: list[str]) -> str:
    return ",".join(t.strip() for t in tags)


@router.get("/", response_model=FAQListResponse, summary="List all FAQ items")
def list_faqs(
    tags: list[str] = Query(default=[], description="Filter by tag(s)"),
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    q = db.query(FAQ)
    if is_active is not None:
        q = q.filter(FAQ.is_active == is_active)
    if tags:
        for tag in tags:
            q = q.filter(FAQ.tags.contains(tag))
    items = q.order_by(FAQ.created_at.desc()).all()
    return FAQListResponse(count=len(items), results=items)


@router.post("/", response_model=FAQResponse, status_code=201, summary="Create a FAQ item")
def create_faq(
    payload: FAQCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    faq = FAQ(
        question=payload.question,
        answer=payload.answer,
        tags=_tags_to_str(payload.tags),
        is_active=payload.is_active,
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


@router.get("/{faq_id}/", response_model=FAQResponse, summary="Get a FAQ item")
def get_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ item not found")
    return faq


@router.put("/{faq_id}/", response_model=FAQResponse, summary="Full update of a FAQ item")
def update_faq(
    faq_id: int,
    payload: FAQUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ item not found")
    faq.question = payload.question
    faq.answer = payload.answer
    faq.tags = _tags_to_str(payload.tags)
    faq.is_active = payload.is_active
    db.commit()
    db.refresh(faq)
    return faq


@router.delete("/{faq_id}/", status_code=204, summary="Delete a FAQ item")
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ item not found")
    db.delete(faq)
    db.commit()
