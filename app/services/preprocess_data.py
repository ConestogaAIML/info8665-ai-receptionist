"""Preprocess raw appointments using feature names from environment secrets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import get_settings
from app.logging_config import configure_application_logging

logger = configure_application_logging()


def preprocess_appointments(
    raw_path: str = "data/raw/appointments.csv",
) -> Path:
    settings = get_settings()
    logger.info(
        "EDA preprocess start experiment=%s v%s features=%s",
        settings.experiment_name,
        settings.experiment_version,
        settings.feature_names,
    )

    df = pd.read_csv(raw_path)
    logger.info("Raw columns: %s", list(df.columns))

    selected_columns = [
        "PatientId",
        "Age",
        "Gender",
        "ScheduledDay",
        "AppointmentDay",
        "SMS_received",
        "No-show",
    ]
    df = df[selected_columns]

    df["ScheduledDay"] = pd.to_datetime(df["ScheduledDay"])
    df["AppointmentDay"] = pd.to_datetime(df["AppointmentDay"])
    df["WaitingDays"] = (df["AppointmentDay"] - df["ScheduledDay"]).dt.days
    df["AppointmentWeekday"] = df["AppointmentDay"].dt.weekday
    df["AppointmentHour"] = df["AppointmentDay"].dt.hour

    features = settings.feature_names
    target = settings.target_column
    df[target] = df[target].map({"Yes": 1, "No": 0})

    missing = [col for col in features if col not in df.columns]
    if missing:
        raise ValueError(f"Cannot build features after EDA; missing: {missing}")

    out = df[["PatientId"] + features + [target]]
    out_path = Path(settings.processed_data_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    logger.info("Wrote processed dataset rows=%s path=%s", len(out), out_path)
    return out_path


if __name__ == "__main__":
    preprocess_appointments()
