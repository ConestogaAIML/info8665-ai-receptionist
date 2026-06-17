from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth import verify_token
from app.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceListResponse, ServiceResponse, ServiceUpdate

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("/", response_model=ServiceListResponse, summary="List all services")
def list_services(
    category: str | None = Query(default=None, description="Filter by category"),
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    q = db.query(Service)
    if category is not None:
        q = q.filter(Service.category == category)
    if is_active is not None:
        q = q.filter(Service.is_active == is_active)
    items = q.order_by(Service.created_at.desc()).all()
    return ServiceListResponse(count=len(items), results=items)


@router.post("/", response_model=ServiceResponse, status_code=201, summary="Create a service")
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    service = Service(
        name=payload.name,
        description=payload.description,
        duration_minutes=payload.duration_minutes,
        price=payload.price,
        category=payload.category,
        is_active=payload.is_active,
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/{service_id}/", response_model=ServiceResponse, summary="Get a service")
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.put("/{service_id}/", response_model=ServiceResponse, summary="Update a service")
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.name = payload.name
    service.description = payload.description
    service.duration_minutes = payload.duration_minutes
    service.price = payload.price
    service.category = payload.category
    service.is_active = payload.is_active
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}/", status_code=204, summary="Delete a service")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()
