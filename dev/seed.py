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

from app.database import Base, SessionLocal, engine
from app.models import Business, BusinessFAQ  # noqa: F401 — registers all tables

Base.metadata.create_all(bind=engine)

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


if __name__ == "__main__":
    print("Seeding database...\n")
    seed()
