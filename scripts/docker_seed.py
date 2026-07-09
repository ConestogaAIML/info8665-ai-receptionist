"""Seed demo clients and services when the container starts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal, ensure_schema
from app.services.demo_seed import seed_appointment_demo_data


def main() -> None:
    ensure_schema()
    db = SessionLocal()
    try:
        result = seed_appointment_demo_data(db)
        print(
            "Demo seed:",
            f"{result['clients_total']} clients,",
            f"{result['services_total']} services,",
            f"{result['appointments_added']} new appointment(s).",
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
