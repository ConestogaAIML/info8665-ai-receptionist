from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.client import Client
from app.models.service import Service

DEMO_CLIENTS = [
    {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "519-555-0100",
        "notes": "Prefers morning appointments.",
    },
    {
        "first_name": "Michael",
        "last_name": "Chen",
        "email": "michael.chen@example.com",
        "phone": "519-555-0101",
        "notes": "Allergic to certain hair dyes.",
    },
]

DEMO_SERVICES = [
    {
        "name": "Classic Haircut",
        "description": "Wash, cut, and style.",
        "duration_minutes": 45,
        "price": 35.00,
        "category": "Hair",
        "is_active": True,
    },
    {
        "name": "Colour & Highlights",
        "description": "Full colour or partial highlights.",
        "duration_minutes": 120,
        "price": 95.00,
        "category": "Hair",
        "is_active": True,
    },
    {
        "name": "Swedish Massage",
        "description": "60-minute relaxation massage.",
        "duration_minutes": 60,
        "price": 80.00,
        "category": "Spa",
        "is_active": True,
    },
]


def seed_appointment_demo_data(db: Session) -> dict:
    clients_added = 0
    services_added = 0
    appointments_added = 0

    client_records: list[Client] = []
    for data in DEMO_CLIENTS:
        existing = db.query(Client).filter(Client.email == data["email"]).first()
        if existing:
            client_records.append(existing)
            continue
        client = Client(**data)
        db.add(client)
        db.flush()
        client_records.append(client)
        clients_added += 1

    service_records: list[Service] = []
    for data in DEMO_SERVICES:
        existing = db.query(Service).filter(Service.name == data["name"]).first()
        if existing:
            service_records.append(existing)
            continue
        service = Service(**data)
        db.add(service)
        db.flush()
        service_records.append(service)
        services_added += 1

    if client_records and service_records:
        sample_date = (date.today() + timedelta(days=1)).isoformat()
        already_booked = (
            db.query(Appointment)
            .filter(
                Appointment.client_id == client_records[0].id,
                Appointment.appointment_date == sample_date,
                Appointment.appointment_time == "10:00",
            )
            .first()
        )
        if not already_booked:
            db.add(
                Appointment(
                    client_id=client_records[0].id,
                    service_id=service_records[0].id,
                    appointment_date=sample_date,
                    appointment_time="10:00",
                    status="scheduled",
                    notes="Sample booking created by demo seed.",
                )
            )
            appointments_added += 1

    db.commit()

    return {
        "message": "Demo appointment data ready.",
        "clients_added": clients_added,
        "services_added": services_added,
        "appointments_added": appointments_added,
        "clients_total": len(client_records),
        "services_total": len(service_records),
    }
