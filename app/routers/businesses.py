from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth import verify_token
from app.database import get_db
from app.models.business import Business
from app.schemas.business import (
    BusinessCreate,
    BusinessListResponse,
    BusinessResponse,
    BusinessUpdate,
)

router = APIRouter(prefix="/api/businesses", tags=["Businesses"])


@router.get("/", response_model=BusinessListResponse, summary="List all businesses")
def list_businesses(
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    q = db.query(Business)
    if is_active is not None:
        q = q.filter(Business.is_active == is_active)
    items = q.order_by(Business.created_at.desc()).all()
    return BusinessListResponse(count=len(items), results=items)


@router.post(
    "/",
    response_model=BusinessResponse,
    status_code=201,
    summary="Create a business",
)
def create_business(
    payload: BusinessCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    business = Business(
        name=payload.name,
        description=payload.description,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        business_hours=payload.business_hours,
        website=payload.website,
        is_active=payload.is_active,
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


@router.get(
    "/{business_id}/",
    response_model=BusinessResponse,
    summary="Get a business",
)
def get_business(
    business_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@router.put(
    "/{business_id}/",
    response_model=BusinessResponse,
    summary="Full update of a business",
)
def update_business(
    business_id: int,
    payload: BusinessUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    business.name = payload.name
    business.description = payload.description
    business.phone = payload.phone
    business.email = payload.email
    business.address = payload.address
    business.business_hours = payload.business_hours
    business.website = payload.website
    business.is_active = payload.is_active
    db.commit()
    db.refresh(business)
    return business


@router.delete("/{business_id}/", status_code=204, summary="Delete a business")
def delete_business(
    business_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    db.delete(business)
    db.commit()
