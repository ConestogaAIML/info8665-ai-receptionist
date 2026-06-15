"""FAQ intent classifier inference service."""

from __future__ import annotations

import os
from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline

_BASE_DIR = Path(__file__).resolve().parent.parent.parent
_DEFAULT_MODEL_PATH = _BASE_DIR / "training" / "faq_classifier.joblib"

_pipeline: Pipeline | None = None
_load_attempted = False


def _model_path() -> Path:
    return Path(os.environ.get("FAQ_MODEL_PATH", str(_DEFAULT_MODEL_PATH)))


def _load_pipeline() -> Pipeline | None:
    global _pipeline, _load_attempted
    if _load_attempted:
        return _pipeline
    _load_attempted = True
    path = _model_path()
    if not path.exists():
        return None
    _pipeline = joblib.load(path)
    return _pipeline


def predict(message: str) -> tuple[str | None, float]:
    """Predict FAQ category and confidence for a user message."""
    pipeline = _load_pipeline()
    if pipeline is None:
        return None, 0.0

    proba = pipeline.predict_proba([message])[0]
    best_idx = int(proba.argmax())
    category = pipeline.classes_[best_idx]
    confidence = float(proba[best_idx])
    return category, confidence


def reset_cache() -> None:
    """Clear cached model (useful in tests)."""
    global _pipeline, _load_attempted
    _pipeline = None
    _load_attempted = False
