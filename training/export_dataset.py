"""
Export FAQ training datasets to local CSV files.

Downloads the Bitext customer-support dataset from Hugging Face (one-time),
remaps categories to this project's labels, and optionally merges with the
custom training file or exports FAQs from the database.

Usage:
    python training/export_dataset.py bitext
    python training/export_dataset.py merge
    python training/export_dataset.py db
    python training/export_dataset.py all
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data-collection"
CUSTOM_CSV = DATA_DIR / "faq_training_data.csv"
BITEXT_CSV = DATA_DIR / "bitext_mapped.csv"
COMBINED_CSV = DATA_DIR / "faq_training_combined.csv"
DB_EXPORT_CSV = DATA_DIR / "faq_from_db.csv"

BITEXT_HF_URL = (
    "hf://datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset/"
    "Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv"
)

# Map Bitext high-level categories to our business FAQ labels.
BITEXT_LABEL_MAP: dict[str, str] = {
    "PAYMENT": "payment",
    "CANCELLATION_FEE": "policy",
    "REFUND": "policy",
    "CONTACT": "booking",
    "ORDER": "booking",
    "DELIVERY": "location",
    "SHIPPING_ADDRESS": "location",
    "FEEDBACK": "policy",
    "INVOICE": "payment",
    "ACCOUNT": "booking",
    "SUBSCRIPTION": "services",
    "NEWSLETTER": "services",
}


def _save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")


def export_bitext(out_path: Path = BITEXT_CSV) -> pd.DataFrame:
    """Download Bitext from Hugging Face, remap labels, save as local CSV."""
    print("Downloading Bitext dataset from Hugging Face...")
    raw = pd.read_csv(BITEXT_HF_URL)

    df = raw[["instruction", "category"]].copy()
    df = df.rename(columns={"instruction": "text", "category": "bitext_category"})
    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = df["bitext_category"].map(BITEXT_LABEL_MAP)
    df = df.dropna(subset=["text", "label"])
    df = df[df["text"] != ""]
    df = df.drop_duplicates(subset=["text", "label"])
    df = df[["text", "label"]].sort_values("label").reset_index(drop=True)

    _save_csv(df, out_path)
    print(f"Label distribution:\n{df['label'].value_counts().to_string()}")
    return df


def export_from_db(out_path: Path = DB_EXPORT_CSV) -> pd.DataFrame:
    """Export active BusinessFAQ rows from SQLite as text/label CSV."""
    sys.path.insert(0, str(BASE_DIR))
    from app.database import SessionLocal
    from app.models.faq import BusinessFAQ

    db = SessionLocal()
    try:
        faqs = (
            db.query(BusinessFAQ)
            .filter(BusinessFAQ.is_active == True)  # noqa: E712
            .all()
        )
        rows = [
            {"text": faq.question.strip(), "label": faq.category.strip()}
            for faq in faqs
            if faq.question.strip() and faq.category.strip()
        ]
    finally:
        db.close()

    df = pd.DataFrame(rows).drop_duplicates(subset=["text", "label"])
    _save_csv(df, out_path)
    return df


def merge_datasets(
    custom_path: Path = CUSTOM_CSV,
    extra_path: Path = BITEXT_CSV,
    out_path: Path = COMBINED_CSV,
) -> pd.DataFrame:
    """Merge custom training CSV with an exported dataset (e.g. Bitext)."""
    frames: list[pd.DataFrame] = []

    if custom_path.exists():
        custom = pd.read_csv(custom_path)
        custom = custom[["text", "label"]].dropna()
        frames.append(custom)
        print(f"Loaded {len(custom)} rows from {custom_path.name}")

    if extra_path.exists():
        extra = pd.read_csv(extra_path)
        extra = extra[["text", "label"]].dropna()
        frames.append(extra)
        print(f"Loaded {len(extra)} rows from {extra_path.name}")
    else:
        print(f"Skipping merge — {extra_path.name} not found. Run: python training/export_dataset.py bitext")

    if not frames:
        raise ValueError("No datasets found to merge")

    combined = pd.concat(frames, ignore_index=True)
    combined["text"] = combined["text"].astype(str).str.strip()
    combined["label"] = combined["label"].astype(str).str.strip()
    combined = combined[(combined["text"] != "") & (combined["label"] != "")]
    combined = combined.drop_duplicates(subset=["text", "label"]).reset_index(drop=True)

    _save_csv(combined, out_path)
    print(f"Label distribution:\n{combined['label'].value_counts().to_string()}")
    return combined


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "all"

    if command == "bitext":
        export_bitext()
    elif command == "db":
        export_from_db()
    elif command == "merge":
        merge_datasets()
    elif command == "all":
        export_bitext()
        merge_datasets()
    else:
        print("Usage: python training/export_dataset.py [bitext|db|merge|all]")
        sys.exit(1)


if __name__ == "__main__":
    main()
