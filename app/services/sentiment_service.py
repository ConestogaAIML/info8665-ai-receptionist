"""
Sentiment Analysis Service
===========================
Implements the ML inference layer for the AI Receptionist sentiment use case.
Uses scikit-learn TF-IDF + Logistic Regression to match the project's existing
ML pipeline (see architecture blueprint: Skil-learn TF-IDF + Logistic).

The service exposes two public functions:
  - analyze(text) → SentimentResult
  - train(records)  → retrains the in-memory model from labelled DB records

In production the trained model artefacts are managed by DVC and loaded from
the ML Training Pipeline; this module falls back to a lightweight default model
when no saved artefacts are found so the API remains runnable from day one.
"""

from __future__ import annotations

import os
import pickle
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

SentimentValue = Literal["positive", "neutral", "negative"]
CategoryValue  = Literal["making_appointment", "cancel_appointment", "ask_question", "other"]

ESCALATE_THRESHOLD = float(os.environ.get("ESCALATE_CONFIDENCE_THRESHOLD", "0.70"))
MODEL_PATH = Path(os.environ.get("SENTIMENT_MODEL_PATH", "./data/sentiment_model.pkl"))


@dataclass
class SentimentResult:
    sentiment: SentimentValue
    emotion: str
    category: CategoryValue
    confidence: float
    escalate: bool
    analyzed_at: datetime


# ---------------------------------------------------------------------------
# Keyword heuristics — used as training seed data and cold-start fallback
# ---------------------------------------------------------------------------

_NEGATIVE_KEYWORDS = {
    "frustrated", "angry", "upset", "cancel", "terrible", "horrible",
    "worst", "awful", "disgusting", "hate", "furious", "disappointed",
    "unacceptable", "ridiculous", "pathetic", "useless", "broken",
}
_POSITIVE_KEYWORDS = {
    "great", "excellent", "wonderful", "happy", "love", "fantastic",
    "perfect", "amazing", "pleased", "satisfied", "good", "nice",
    "thanks", "thank you", "appreciate",
}
_APPT_KEYWORDS   = {"book", "booking", "schedule", "appointment", "reserve", "slot", "reschedule"}
_CANCEL_KEYWORDS = {"cancel", "cancellation", "remove", "delete my appointment", "called off"}
_FAQ_KEYWORDS    = {"hours", "open", "price", "cost", "location", "address", "how", "what", "when", "where", "do you"}

_EMOTION_MAP = {
    "negative": {
        frozenset(["frustrated", "angry", "furious", "upset"]): "frustrated",
        frozenset(["disappointed", "sad", "terrible", "awful"]):  "disappointed",
        frozenset(["unacceptable", "ridiculous", "pathetic"]):    "indignant",
    },
    "positive": {
        frozenset(["happy", "pleased", "satisfied", "great", "wonderful"]): "happy",
        frozenset(["thanks", "thank you", "appreciate"]):                    "grateful",
    },
    "neutral": {},
}


def _keyword_sentiment(tokens: set[str]) -> tuple[SentimentValue, str, float]:
    neg = len(tokens & _NEGATIVE_KEYWORDS)
    pos = len(tokens & _POSITIVE_KEYWORDS)
    total = neg + pos or 1
    if neg > pos:
        conf = min(0.60 + 0.08 * neg, 0.90)
        emotion = "frustrated" if "frustrated" in tokens or "angry" in tokens else "negative"
        return "negative", emotion, conf
    if pos > neg:
        conf = min(0.60 + 0.08 * pos, 0.90)
        emotion = "grateful" if ("thanks" in tokens or "thank you" in tokens) else "happy"
        return "positive", emotion, conf
    return "neutral", "calm", 0.55


def _keyword_category(text_lower: str) -> CategoryValue:
    if any(k in text_lower for k in _CANCEL_KEYWORDS):
        return "cancel_appointment"
    if any(k in text_lower for k in _APPT_KEYWORDS):
        return "making_appointment"
    if any(k in text_lower for k in _FAQ_KEYWORDS):
        return "ask_question"
    return "other"


# ---------------------------------------------------------------------------
# Model wrapper
# ---------------------------------------------------------------------------

class _SentimentModel:
    """Wraps sklearn pipeline; falls back to keyword heuristics if not trained."""

    def __init__(self) -> None:
        self._sentiment_pipeline = None
        self._category_pipeline  = None
        self._load()

    def _load(self) -> None:
        if MODEL_PATH.exists():
            try:
                with MODEL_PATH.open("rb") as f:
                    data = pickle.load(f)
                self._sentiment_pipeline = data.get("sentiment")
                self._category_pipeline  = data.get("category")
            except Exception:
                pass  # fall back to heuristics silently

    def _save(self) -> None:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with MODEL_PATH.open("wb") as f:
            pickle.dump(
                {"sentiment": self._sentiment_pipeline, "category": self._category_pipeline},
                f,
            )

    def train(self, texts: list[str], sentiments: list[str], categories: list[str]) -> None:
        """Retrain the TF-IDF + Logistic Regression pipeline from labelled data."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline

        self._sentiment_pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
            ("clf",   LogisticRegression(max_iter=500, C=1.0)),
        ])
        self._sentiment_pipeline.fit(texts, sentiments)

        self._category_pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
            ("clf",   LogisticRegression(max_iter=500, C=1.0)),
        ])
        self._category_pipeline.fit(texts, categories)
        self._save()

    def predict(self, text: str) -> SentimentResult:
        text_lower = text.lower()
        tokens = set(text_lower.split())

        if self._sentiment_pipeline and self._category_pipeline:
            sentiment: SentimentValue = self._sentiment_pipeline.predict([text])[0]
            proba = self._sentiment_pipeline.predict_proba([text])[0]
            confidence = float(max(proba))
            category: CategoryValue = self._category_pipeline.predict([text])[0]
            # Derive emotion from keyword heuristics (faster than a 3rd model)
            _, emotion, _ = _keyword_sentiment(tokens)
        else:
            sentiment, emotion, confidence = _keyword_sentiment(tokens)
            category = _keyword_category(text_lower)

        escalate = (sentiment == "negative") and (confidence >= ESCALATE_THRESHOLD)

        return SentimentResult(
            sentiment=sentiment,
            emotion=emotion,
            category=category,
            confidence=round(confidence, 4),
            escalate=escalate,
            analyzed_at=datetime.now(timezone.utc),
        )


# Singleton shared across requests
_model = _SentimentModel()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze(text: str) -> SentimentResult:
    """Run inference on a single conversation text."""
    return _model.predict(text)


def retrain(texts: list[str], sentiments: list[str], categories: list[str]) -> None:
    """Retrain the model from corrected / newly labelled data stored in the DB."""
    if len(texts) < 10:
        raise ValueError("Need at least 10 labelled samples to retrain.")
    _model.train(texts, sentiments, categories)
