"""Train the appointment no-show model using secrets-managed hyperparameters."""

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from app.config import get_settings
from app.logging_config import configure_application_logging

logger = configure_application_logging()


def train_no_show_model() -> dict:
    settings = get_settings()
    logger.info(
        "Starting experiment %s v%s (expected_accuracy=%.3f, epochs=%s)",
        settings.experiment_name,
        settings.experiment_version,
        settings.expected_accuracy,
        settings.ml_epochs,
    )
    logger.info(
        "Hyperparameters n_estimators=%s max_depth=%s test_size=%s random_state=%s",
        settings.ml_n_estimators,
        settings.ml_max_depth,
        settings.ml_test_size,
        settings.ml_random_state,
    )
    logger.info("EDA feature names from secrets: %s", settings.feature_names)

    data_path = Path(settings.processed_data_path)
    if not data_path.exists():
        raise FileNotFoundError(f"Processed data not found: {data_path}")

    df = pd.read_csv(data_path)
    missing = [col for col in settings.feature_names if col not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns in dataset: {missing}")
    if settings.target_column not in df.columns:
        raise ValueError(f"Missing target column: {settings.target_column}")

    X = df[settings.feature_names]
    y = df[settings.target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=settings.ml_test_size,
        random_state=settings.ml_random_state,
    )

    # RandomForest does not use gradient epochs; ML_EPOCHS is experiment metadata
    # and used here to log iterative training progress for DevOps tracking.
    model = RandomForestClassifier(
        n_estimators=settings.ml_n_estimators,
        max_depth=settings.ml_max_depth,
        random_state=settings.ml_random_state,
        n_jobs=-1,
    )

    for epoch in range(1, settings.ml_epochs + 1):
        model.fit(X_train, y_train)
        interim = accuracy_score(y_test, model.predict(X_test))
        logger.info(
            "Experiment %s epoch %s/%s interim_accuracy=%.4f",
            settings.experiment_name,
            epoch,
            settings.ml_epochs,
            interim,
        )

    accuracy = accuracy_score(y_test, model.predict(X_test))
    model_path = Path(settings.model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    met_expectation = accuracy >= settings.expected_accuracy
    logger.info(
        "Experiment %s v%s finished accuracy=%.4f expected=%.4f met_expectation=%s path=%s",
        settings.experiment_name,
        settings.experiment_version,
        accuracy,
        settings.expected_accuracy,
        met_expectation,
        model_path,
    )

    return {
        "experiment_name": settings.experiment_name,
        "experiment_version": settings.experiment_version,
        "accuracy": float(accuracy),
        "expected_accuracy": settings.expected_accuracy,
        "met_expectation": met_expectation,
        "epochs": settings.ml_epochs,
        "feature_names": settings.feature_names,
        "model_path": str(model_path),
    }


if __name__ == "__main__":
    result = train_no_show_model()
    print(result)
