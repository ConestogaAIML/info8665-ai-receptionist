"""Evaluate the no-show model against secrets-managed expected accuracy."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from app.config import get_settings
from app.logging_config import configure_application_logging

logger = configure_application_logging()


def evaluate_no_show_model() -> dict:
    settings = get_settings()
    logger.info(
        "Evaluating experiment %s v%s against expected_accuracy=%.3f",
        settings.experiment_name,
        settings.experiment_version,
        settings.expected_accuracy,
    )

    df = pd.read_csv(settings.processed_data_path)
    X = df[settings.feature_names]
    y = df[settings.target_column]

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=settings.ml_test_size,
        random_state=settings.ml_random_state,
    )

    model_path = Path(settings.model_path)
    model = joblib.load(model_path)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    met = accuracy >= settings.expected_accuracy

    logger.info(
        "Evaluation accuracy=%.4f expected=%.4f met_expectation=%s",
        accuracy,
        settings.expected_accuracy,
        met,
    )
    print("Accuracy:", accuracy)
    print("Expected:", settings.expected_accuracy)
    print("Met expectation:", met)
    return {
        "accuracy": float(accuracy),
        "expected_accuracy": settings.expected_accuracy,
        "met_expectation": met,
        "experiment_name": settings.experiment_name,
        "experiment_version": settings.experiment_version,
    }


if __name__ == "__main__":
    evaluate_no_show_model()
