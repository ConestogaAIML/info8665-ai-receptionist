"""Business rules that gate appointment booking."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.appointment import Appointment

SKIP_REBOOK_COOLDOWN_DAYS = 14


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def latest_skip_marked_at(db: Session, client_id: int) -> datetime | None:
    """When the client's most recent skip was marked (appointment updated_at)."""
    skipped = (
        db.query(Appointment)
        .filter(
            Appointment.client_id == client_id,
            Appointment.status == "no_show",
        )
        .order_by(Appointment.updated_at.desc())
        .first()
    )
    if skipped is None or skipped.updated_at is None:
        return None
    return _as_utc(skipped.updated_at)


def rebook_eligible_at(db: Session, client_id: int) -> datetime | None:
    """Earliest UTC time the client may be booked again, or None if unrestricted."""
    skipped_at = latest_skip_marked_at(db, client_id)
    if skipped_at is None:
        return None
    return skipped_at + timedelta(days=SKIP_REBOOK_COOLDOWN_DAYS)


def assert_client_rebookable(db: Session, client_id: int) -> None:
    """
    Block booking when the client was marked skipped within the last 2 weeks.

    Applies to everyone (manager or customer-facing booking paths that hit this check).
    """
    eligible_at = rebook_eligible_at(db, client_id)
    if eligible_at is None:
        return

    now = datetime.now(timezone.utc)
    if now >= eligible_at:
        return

    raise HTTPException(
        status_code=409,
        detail=(
            "This client skipped an appointment and cannot be booked again until "
            f"{eligible_at.date().isoformat()} "
            f"({SKIP_REBOOK_COOLDOWN_DAYS}-day cooldown after skip)."
        ),
    )
