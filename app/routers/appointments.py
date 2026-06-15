from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.auth import verify_token
from app.database import get_db
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.service import Service
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentUpdate,
)

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


def _to_response(appt: Appointment) -> dict:
    """Build a plain dict for AppointmentResponse, embedding client/service names."""
    return {
        "id": appt.id,
        "client_id": appt.client_id,
        "service_id": appt.service_id,
        "client_name": f"{appt.client.first_name} {appt.client.last_name}",
        "service_name": appt.service.name,
        "appointment_date": appt.appointment_date,
        "appointment_time": appt.appointment_time,
        "status": appt.status,
        "notes": appt.notes,
        "created_at": appt.created_at,
        "updated_at": appt.updated_at,
    }


def _load(db: Session, appointment_id: int) -> Appointment:
    """Fetch an appointment with relationships eagerly loaded."""
    return (
        db.query(Appointment)
        .options(joinedload(Appointment.client), joinedload(Appointment.service))
        .filter(Appointment.id == appointment_id)
        .first()
    )


@router.get("/", response_model=AppointmentListResponse, summary="List all appointments")
def list_appointments(
    appointment_date: str | None = Query(default=None, description="Filter by date (YYYY-MM-DD)"),
    status: str | None = Query(default=None, description="Filter by status"),
    client_id: int | None = Query(default=None, description="Filter by client ID"),
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    q = db.query(Appointment).options(
        joinedload(Appointment.client), joinedload(Appointment.service)
    )
    if appointment_date:
        q = q.filter(Appointment.appointment_date == appointment_date)
    if status:
        q = q.filter(Appointment.status == status)
    if client_id is not None:
        q = q.filter(Appointment.client_id == client_id)
    items = q.order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    results = [AppointmentResponse.model_validate(_to_response(a)) for a in items]
    return AppointmentListResponse(count=len(results), results=results)


@router.post("/", response_model=AppointmentResponse, status_code=201, summary="Create an appointment")
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    if not db.query(Client).filter(Client.id == payload.client_id).first():
        raise HTTPException(status_code=404, detail="Client not found")
    if not db.query(Service).filter(Service.id == payload.service_id).first():
        raise HTTPException(status_code=404, detail="Service not found")
    appt = Appointment(
        client_id=payload.client_id,
        service_id=payload.service_id,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(appt)
    db.commit()
    appt = _load(db, appt.id)
    return AppointmentResponse.model_validate(_to_response(appt))


@router.get("/{appointment_id}/", response_model=AppointmentResponse, summary="Get an appointment")
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    appt = _load(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return AppointmentResponse.model_validate(_to_response(appt))


@router.put("/{appointment_id}/", response_model=AppointmentResponse, summary="Update an appointment")
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if payload.client_id != appt.client_id:
        if not db.query(Client).filter(Client.id == payload.client_id).first():
            raise HTTPException(status_code=404, detail="Client not found")
    if payload.service_id != appt.service_id:
        if not db.query(Service).filter(Service.id == payload.service_id).first():
            raise HTTPException(status_code=404, detail="Service not found")
    appt.client_id = payload.client_id
    appt.service_id = payload.service_id
    appt.appointment_date = payload.appointment_date
    appt.appointment_time = payload.appointment_time
    appt.status = payload.status
    appt.notes = payload.notes
    db.commit()
    appt = _load(db, appointment_id)
    return AppointmentResponse.model_validate(_to_response(appt))


@router.delete("/{appointment_id}/", status_code=204, summary="Delete an appointment")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(appt)
    db.commit()
