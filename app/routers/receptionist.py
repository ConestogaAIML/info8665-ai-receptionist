from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.visitor import Visitor
from app.schemas.receptionist import VisitorRequest, VisitorResponse

router = APIRouter(prefix="/receptionist", tags=["Receptionist"])


@router.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@router.post("/greet", response_model=VisitorResponse, status_code=201, summary="Check in a visitor")
def greet_visitor(payload: VisitorRequest, db: Session = Depends(get_db)):
    visitor = Visitor(name=payload.name, purpose=payload.purpose, host=payload.host)
    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    return visitor


@router.get("/visitors", response_model=list[VisitorResponse], summary="List all visitors")
def list_visitors(db: Session = Depends(get_db)):
    return db.query(Visitor).order_by(Visitor.created_at.desc()).all()


@router.get("/visitors/{visitor_id}", response_model=VisitorResponse, summary="Get visitor by ID")
def get_visitor(visitor_id: int, db: Session = Depends(get_db)):
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor


@router.delete("/visitors/{visitor_id}", status_code=204, summary="Check out a visitor")
def delete_visitor(visitor_id: int, db: Session = Depends(get_db)):
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    db.delete(visitor)
    db.commit()
