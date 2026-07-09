"""
Seed script — populates the database with sample Business and BusinessFAQ data.
Safe to re-run: skips records that already exist (matched by name / question).

Usage:
    python dev/seed.py
"""

import sys
import os

# Allow running from the project root without installing the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, SessionLocal, engine, ensure_schema
from app.models import Business, BusinessFAQ, Client, Service, Appointment  # noqa: F401

ensure_schema()

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

BUSINESSES = [
    {
        "name": "Bella Hair Studio",
        "description": (
            "A full-service hair salon specializing in cuts, colour, and styling "
            "for all hair types."
        ),
        "phone": "519-555-0101",
        "email": "info@bellahairstudio.com",
        "address": "123 Main St, Waterloo, ON N2L 3G1",
        "business_hours": "Mon–Fri 9 am–6 pm · Sat 10 am–4 pm · Sun Closed",
        "website": "https://bellahairstudio.com",
        "is_active": True,
        "faqs": [
            {
                "question": "What are your business hours?",
                "answer": (
                    "We are open Monday to Friday 9 AM–6 PM and Saturday 10 AM–4 PM. "
                    "We are closed on Sundays."
                ),
                "category": "hours",
                "tags": "hours,general",
            },
            {
                "question": "Where are you located?",
                "answer": "We are at 123 Main St, Waterloo, ON N2L 3G1, near Uptown Waterloo.",
                "category": "location",
                "tags": "location,address",
            },
            {
                "question": "How do I book an appointment?",
                "answer": (
                    "You can book online through our website, call us at 519-555-0101, "
                    "or send an email to info@bellahairstudio.com."
                ),
                "category": "booking",
                "tags": "booking,appointment",
            },
            {
                "question": "What is your cancellation policy?",
                "answer": (
                    "We ask for at least 24 hours' notice for cancellations or rescheduling. "
                    "Late cancellations may incur a 50% service fee."
                ),
                "category": "policy",
                "tags": "policy,cancellation",
            },
            {
                "question": "Do you offer colour services?",
                "answer": (
                    "Yes! We offer a full range of colour services including highlights, "
                    "balayage, full colour, and toning. Prices vary by length and technique."
                ),
                "category": "services",
                "tags": "services,colour,pricing",
            },
            {
                "question": "Do you accept walk-ins?",
                "answer": (
                    "Walk-ins are welcome based on availability, but we recommend booking "
                    "in advance to secure your preferred time."
                ),
                "category": "booking",
                "tags": "booking,walk-in",
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept cash, debit, Visa, and Mastercard. We do not accept American Express.",
                "category": "payment",
                "tags": "payment,billing",
            },
            {
                "question": "Is parking available?",
                "answer": (
                    "Free street parking is available on Main St. There is also a paid "
                    "municipal parking lot one block away on Erb St."
                ),
                "category": "location",
                "tags": "location,parking",
            },
        ],
    },
    {
        "name": "Serenity Spa & Wellness",
        "description": (
            "A boutique day spa offering massage, facial, and body treatments "
            "in a tranquil environment."
        ),
        "phone": "519-555-0202",
        "email": "hello@serenityspa.ca",
        "address": "456 King St N, Waterloo, ON N2J 2Y9",
        "business_hours": "Tue–Sat 10 am–7 pm · Sun 11 am–5 pm · Mon Closed",
        "website": "https://serenityspa.ca",
        "is_active": True,
        "faqs": [
            {
                "question": "What are your opening hours?",
                "answer": (
                    "We are open Tuesday to Saturday 10 AM–7 PM and Sunday 11 AM–5 PM. "
                    "We are closed on Mondays."
                ),
                "category": "hours",
                "tags": "hours,general",
            },
            {
                "question": "What types of massages do you offer?",
                "answer": (
                    "We offer Swedish, deep tissue, hot stone, prenatal, and sports massage. "
                    "Sessions are available in 60-minute and 90-minute durations."
                ),
                "category": "services",
                "tags": "services,massage",
            },
            {
                "question": "How early should I arrive for my appointment?",
                "answer": (
                    "Please arrive 10–15 minutes before your scheduled time to complete a "
                    "short intake form and begin your relaxation experience."
                ),
                "category": "booking",
                "tags": "booking,arrival",
            },
            {
                "question": "Do you sell gift cards?",
                "answer": (
                    "Yes! Gift cards are available in any denomination, both in-studio and "
                    "on our website. They never expire."
                ),
                "category": "services",
                "tags": "services,gift-cards",
            },
            {
                "question": "Are your products cruelty-free?",
                "answer": (
                    "Absolutely. We exclusively use cruelty-free, plant-based products "
                    "from certified Canadian and European brands."
                ),
                "category": "policy",
                "tags": "policy,products,ethical",
            },
            {
                "question": "What is your late arrival policy?",
                "answer": (
                    "If you arrive late, your session will be shortened accordingly to avoid "
                    "affecting the next guest. The full service price still applies."
                ),
                "category": "policy",
                "tags": "policy,late,arrival",
            },
        ],
    },
]

CLIENTS = [
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

SERVICES = [
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

# ---------------------------------------------------------------------------
# Insert helpers
# ---------------------------------------------------------------------------


def seed():
    db = SessionLocal()
    try:
        total_businesses = 0
        total_faqs = 0

        for biz_data in BUSINESSES:
            faqs_data = biz_data.pop("faqs")

            existing = db.query(Business).filter(Business.name == biz_data["name"]).first()
            if existing:
                print(f"  [skip] Business already exists: {biz_data['name']}")
                business = existing
            else:
                business = Business(**biz_data)
                db.add(business)
                db.flush()  # get business.id before committing
                print(f"  [add]  Business: {business.name} (id={business.id})")
                total_businesses += 1

            for faq_data in faqs_data:
                exists = (
                    db.query(BusinessFAQ)
                    .filter(
                        BusinessFAQ.business_id == business.id,
                        BusinessFAQ.question == faq_data["question"],
                    )
                    .first()
                )
                if exists:
                    print(f"         [skip] FAQ already exists: {faq_data['question'][:60]}")
                    continue

                faq = BusinessFAQ(business_id=business.id, **faq_data)
                db.add(faq)
                print(f"         [add]  FAQ: {faq_data['question'][:60]}")
                total_faqs += 1

        db.commit()
        print(f"\nDone — added {total_businesses} business(es) and {total_faqs} FAQ(s).")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_appointments():
    from datetime import date, timedelta

    db = SessionLocal()
    try:
        clients_added = 0
        services_added = 0
        appointments_added = 0
        client_records = []

        for data in CLIENTS:
            existing = db.query(Client).filter(Client.email == data["email"]).first()
            if existing:
                client_records.append(existing)
                print(f"  [skip] Client already exists: {data['email']}")
                continue
            client = Client(**data)
            db.add(client)
            db.flush()
            client_records.append(client)
            clients_added += 1
            print(f"  [add]  Client: {data['first_name']} {data['last_name']}")

        service_records = []
        for data in SERVICES:
            existing = db.query(Service).filter(Service.name == data["name"]).first()
            if existing:
                service_records.append(existing)
                print(f"  [skip] Service already exists: {data['name']}")
                continue
            service = Service(**data)
            db.add(service)
            db.flush()
            service_records.append(service)
            services_added += 1
            print(f"  [add]  Service: {data['name']}")

        if client_records and service_records:
            sample_date = (date.today() + timedelta(days=1)).isoformat()
            exists = (
                db.query(Appointment)
                .filter(
                    Appointment.client_id == client_records[0].id,
                    Appointment.appointment_date == sample_date,
                )
                .first()
            )
            if not exists:
                db.add(
                    Appointment(
                        client_id=client_records[0].id,
                        service_id=service_records[0].id,
                        appointment_date=sample_date,
                        appointment_time="10:00",
                        status="scheduled",
                        notes="Sample booking from seed script.",
                    )
                )
                appointments_added += 1
                print(f"  [add]  Appointment: {sample_date} 10:00")

        db.commit()
        print(
            f"\nDone — added {clients_added} client(s), {services_added} service(s), "
            f"{appointments_added} appointment(s)."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the AI Receptionist database.")
    parser.add_argument(
        "--appointments",
        action="store_true",
        help="Also seed demo clients, services, and a sample appointment.",
    )
    args = parser.parse_args()

    print("Seeding database...\n")
    seed()
    if args.appointments:
        print("\nSeeding appointment demo data...\n")
        seed_appointments()
