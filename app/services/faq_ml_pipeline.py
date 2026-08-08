"""FAQ ML Ops pipeline stages callable from API services."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.logging_config import configure_application_logging
from app.services import faq_classifier

logger = configure_application_logging()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data-collection"
CUSTOM_CSV = DATA_DIR / "faq_training_data.csv"
COMBINED_CSV = DATA_DIR / "faq_training_combined.csv"
BITEXT_CSV = DATA_DIR / "bitext_mapped.csv"
MODEL_PATH = BASE_DIR / "training" / "faq_classifier.joblib"
EDA_REPORT_PATH = DATA_DIR / "faq_eda_summary.json"


def _export_from_db_local() -> Path:
    """Export active FAQs from DB without importing training package."""
    from app.database import SessionLocal
    from app.models.faq import BusinessFAQ

    out = DATA_DIR / "faq_from_db.csv"
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
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return out


def _merge_local(extra: Path | None = None) -> Path:
    frames: list[pd.DataFrame] = []
    for path in (CUSTOM_CSV, BITEXT_CSV, extra):
        if path is None or not path.exists():
            continue
        part = pd.read_csv(path)[["text", "label"]].dropna()
        frames.append(part)
    if not frames:
        raise FileNotFoundError("No FAQ datasets available to merge")
    combined = pd.concat(frames, ignore_index=True)
    combined["text"] = combined["text"].astype(str).str.strip()
    combined["label"] = combined["label"].astype(str).str.strip()
    combined = combined[(combined["text"] != "") & (combined["label"] != "")]
    combined = combined.drop_duplicates(subset=["text", "label"]).reset_index(drop=True)
    COMBINED_CSV.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(COMBINED_CSV, index=False)
    return COMBINED_CSV


def collect_faq_training_data(source: str = "local") -> dict:
    """
    Data-collection stage: ensure a training CSV exists.

    source=local uses existing combined/custom CSVs (offline-safe for Docker).
    source=db merges FAQs from the application database into the combined CSV.
    """
    logger.info("FAQ pipeline START stage=data_collection source=%s", source)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if source == "db":
        db_csv = _export_from_db_local()
        path = _merge_local(extra=db_csv)
    else:
        if not COMBINED_CSV.exists():
            path = (
                _merge_local()
                if (CUSTOM_CSV.exists() or BITEXT_CSV.exists())
                else CUSTOM_CSV
            )
        else:
            path = COMBINED_CSV

    if not path.exists():
        logger.error("FAQ pipeline END stage=data_collection status=error")
        raise FileNotFoundError(f"FAQ training CSV not found: {path}")

    rows = sum(1 for _ in path.open(encoding="utf-8")) - 1
    result = {
        "stage": "data_collection",
        "source": source,
        "dataset_path": str(path),
        "row_count": max(rows, 0),
        "status": "ok",
    }
    logger.info(
        "FAQ pipeline END stage=data_collection path=%s rows=%s",
        path,
        result["row_count"],
    )
    return result


def eda_faq_dataset(csv_path: str | None = None) -> dict:
    """Exploratory data analysis over the FAQ training set."""
    logger.info("FAQ pipeline START stage=eda")
    path = Path(csv_path) if csv_path else (
        COMBINED_CSV if COMBINED_CSV.exists() else CUSTOM_CSV
    )
    if not path.exists():
        logger.error("FAQ pipeline END stage=eda status=error missing=%s", path)
        raise FileNotFoundError(f"FAQ dataset not found: {path}")

    df = pd.read_csv(path)
    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip()
    df = df[(df["text"] != "") & (df["label"] != "")]

    label_counts = df["label"].value_counts().to_dict()
    result = {
        "stage": "eda",
        "dataset_path": str(path),
        "row_count": int(len(df)),
        "unique_labels": int(df["label"].nunique()),
        "label_distribution": {str(k): int(v) for k, v in label_counts.items()},
        "avg_text_length": float(df["text"].str.len().mean()) if len(df) else 0.0,
        "status": "ok",
    }
    EDA_REPORT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info(
        "FAQ pipeline END stage=eda rows=%s labels=%s",
        result["row_count"],
        result["unique_labels"],
    )
    return result


def preprocess_faq_dataset(csv_path: str | None = None) -> dict:
    """Light preprocessing: drop empties/duplicates and rewrite the combined CSV."""
    logger.info("FAQ pipeline START stage=preprocess")
    path = Path(csv_path) if csv_path else (
        COMBINED_CSV if COMBINED_CSV.exists() else CUSTOM_CSV
    )
    if not path.exists():
        logger.error("FAQ pipeline END stage=preprocess status=error")
        raise FileNotFoundError(f"FAQ dataset not found: {path}")

    before = pd.read_csv(path)
    df = before[["text", "label"]].copy()
    df["text"] = df["text"].astype(str).str.strip().str.lower()
    df["label"] = df["label"].astype(str).str.strip().str.lower()
    df = df[(df["text"] != "") & (df["label"] != "")]
    df = df.drop_duplicates(subset=["text", "label"]).reset_index(drop=True)
    out = COMBINED_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    result = {
        "stage": "preprocess",
        "input_path": str(path),
        "output_path": str(out),
        "rows_before": int(len(before)),
        "rows_after": int(len(df)),
        "status": "ok",
    }
    logger.info(
        "FAQ pipeline END stage=preprocess before=%s after=%s",
        result["rows_before"],
        result["rows_after"],
    )
    return result


def train_faq_model(csv_path: str | None = None) -> dict:
    """Train TF-IDF + LogisticRegression FAQ classifier and persist artifact."""
    logger.info("FAQ pipeline START stage=train")
    path = Path(csv_path) if csv_path else (
        COMBINED_CSV if COMBINED_CSV.exists() else CUSTOM_CSV
    )
    if not path.exists():
        logger.error("FAQ pipeline END stage=train status=error")
        raise FileNotFoundError(f"FAQ dataset not found: {path}")

    texts: list[str] = []
    labels: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip()
            if text and label:
                texts.append(text)
                labels.append(label)

    if len(texts) < 10:
        raise ValueError("Need at least 10 labeled FAQ rows to train")

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english")),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    stratify = labels if len(set(labels)) > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=stratify,
    )
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    accuracy = float(accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    faq_classifier.reset_cache()

    result = {
        "stage": "train",
        "dataset_path": str(path),
        "model_path": str(MODEL_PATH),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": accuracy,
        "classes": sorted(set(labels)),
        "classification_report": report,
        "status": "ok",
    }
    logger.info(
        "FAQ pipeline END stage=train accuracy=%.4f model=%s",
        accuracy,
        MODEL_PATH,
    )
    return result


def validate_faq_model(csv_path: str | None = None) -> dict:
    """Validation stage: score holdout accuracy against the saved model."""
    logger.info("FAQ pipeline START stage=validate")
    if not MODEL_PATH.exists():
        logger.error("FAQ pipeline END stage=validate status=error missing model")
        raise FileNotFoundError(f"FAQ model not found: {MODEL_PATH}")

    path = Path(csv_path) if csv_path else (
        COMBINED_CSV if COMBINED_CSV.exists() else CUSTOM_CSV
    )
    texts: list[str] = []
    labels: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip()
            if text and label:
                texts.append(text)
                labels.append(label)

    stratify = labels if len(set(labels)) > 1 else None
    _, X_test, _, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=stratify,
    )
    model = joblib.load(MODEL_PATH)
    accuracy = float(accuracy_score(y_test, model.predict(X_test)))
    expected = 0.70
    result = {
        "stage": "validate",
        "model_path": str(MODEL_PATH),
        "test_samples": len(X_test),
        "accuracy": accuracy,
        "expected_accuracy": expected,
        "met_expectation": accuracy >= expected,
        "status": "ok",
    }
    logger.info(
        "FAQ pipeline END stage=validate accuracy=%.4f met=%s",
        accuracy,
        result["met_expectation"],
    )
    return result


def reload_faq_model() -> dict:
    """Model serving reload: clear in-process cache so inference loads new artifact."""
    logger.info("FAQ pipeline START stage=reload")
    faq_classifier.reset_cache()
    loaded = faq_classifier._load_pipeline() is not None  # noqa: SLF001
    result = {
        "stage": "reload",
        "model_path": str(MODEL_PATH),
        "loaded": loaded,
        "status": "ok" if loaded else "missing_model",
    }
    logger.info("FAQ pipeline END stage=reload loaded=%s", loaded)
    return result
