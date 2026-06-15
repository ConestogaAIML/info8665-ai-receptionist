"""
Train a TF-IDF + LogisticRegression FAQ intent classifier.

Usage:
    python training/train_faq_classifier.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CSV = BASE_DIR / "data-collection" / "faq_training_data.csv"
DEFAULT_MODEL = BASE_DIR / "training" / "faq_classifier.joblib"


def load_data(csv_path: Path) -> tuple[list[str], list[str]]:
    texts: list[str] = []
    labels: list[str] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row["text"].strip()
            label = row["label"].strip()
            if text and label:
                texts.append(text)
                labels.append(label)
    if not texts:
        raise ValueError(f"No training rows found in {csv_path}")
    return texts, labels


def train(csv_path: Path, model_out: Path) -> Pipeline:
    texts, labels = load_data(csv_path)

    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(ngram_range=(1, 2), stop_words="english"),
            ),
            (
                "clf",
                LogisticRegression(max_iter=1000, class_weight="balanced"),
            ),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Training samples: {len(X_train)}")
    print(f"Test samples:     {len(X_test)}")
    print(f"Accuracy:         {accuracy:.3f}")
    print()
    print(classification_report(y_test, y_pred))

    model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_out)
    print(f"Model saved to {model_out}")
    return pipeline


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    model_out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MODEL
    train(csv_path, model_out)
