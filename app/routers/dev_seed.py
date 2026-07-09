from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import get_db
from app.services.demo_seed import seed_appointment_demo_data

router = APIRouter(prefix="/api/dev", tags=["Dev Tools"])


@router.post("/seed-appointments/", summary="Seed demo clients, services, and a sample appointment")
def seed_appointment_demo(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    return seed_appointment_demo_data(db)
