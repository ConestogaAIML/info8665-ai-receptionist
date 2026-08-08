from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from app.models.appointment import Appointment
from app.models.client import Client
from app.models.service import Service
from app.services.appointment_booking_rules import (
    SKIP_REBOOK_COOLDOWN_DAYS,
    assert_client_rebookable,
    rebook_eligible_at,
)


def _seed_client_service(db):
    client = Client(
        first_name="Daniel",
        last_name="Chen",
        email="daniel@example.com",
        phone="555-0100",
    )
    service = Service(
        name="Haircut",
        description="",
        duration_minutes=30,
        price=40.0,
        category="Hair",
    )
    db.add(client)
    db.add(service)
    db.commit()
    db.refresh(client)
    db.refresh(service)
    return client, service


class TestSkipRebookCooldown:
    def test_no_skip_allows_booking(self, db):
        client, _ = _seed_client_service(db)
        assert_client_rebookable(db, client.id)
        assert rebook_eligible_at(db, client.id) is None

    def test_recent_skip_blocks_booking(self, db):
        client, service = _seed_client_service(db)
        db.add(
            Appointment(
                client_id=client.id,
                service_id=service.id,
                appointment_date="2026-08-01",
                appointment_time="10:00",
                status="no_show",
            )
        )
        db.commit()

        eligible = rebook_eligible_at(db, client.id)
        assert eligible is not None
        assert eligible > datetime.now(timezone.utc)

        try:
            assert_client_rebookable(db, client.id)
            assert False, "expected HTTPException"
        except HTTPException as exc:
            assert exc.status_code == 409
            assert "cannot be booked again until" in exc.detail
            assert str(SKIP_REBOOK_COOLDOWN_DAYS) in exc.detail

    def test_create_appointment_api_enforces_cooldown(self, client, auth_headers, db):
        seeded_client, seeded_service = _seed_client_service(db)
        db.add(
            Appointment(
                client_id=seeded_client.id,
                service_id=seeded_service.id,
                appointment_date="2026-08-01",
                appointment_time="10:00",
                status="no_show",
            )
        )
        db.commit()

        resp = client.post(
            "/api/appointments/",
            headers=auth_headers,
            json={
                "client_id": seeded_client.id,
                "service_id": seeded_service.id,
                "appointment_date": "2026-08-20",
                "appointment_time": "11:00",
                "status": "scheduled",
                "notes": "",
            },
        )
        assert resp.status_code == 409
        assert "cannot be booked again until" in resp.json()["detail"]

    def test_cooldown_expires_after_two_weeks(self, db):
        client, service = _seed_client_service(db)
        old = datetime.now(timezone.utc) - timedelta(days=SKIP_REBOOK_COOLDOWN_DAYS + 1)
        appt = Appointment(
            client_id=client.id,
            service_id=service.id,
            appointment_date="2026-07-01",
            appointment_time="10:00",
            status="no_show",
        )
        db.add(appt)
        db.commit()
        db.refresh(appt)
        # Force updated_at behind the cooldown window (SQLite may rewrite onupdate).
        db.query(Appointment).filter(Appointment.id == appt.id).update(
            {"updated_at": old},
            synchronize_session=False,
        )
        db.commit()

        assert_client_rebookable(db, client.id)
