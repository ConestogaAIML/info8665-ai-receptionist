"""Central secrets and experiment configuration loaded from environment variables.

Values are never hard-coded in business logic. Copy `.env.example` to `.env`
and override locally; Docker Compose injects the same keys at runtime.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root when present (local runs). Docker relies on compose env.
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _get_int(key: str, default: int) -> int:
    raw = os.environ.get(key)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _get_float(key: str, default: float) -> float:
    raw = os.environ.get(key)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


def _get_list(key: str, default: list[str]) -> list[str]:
    raw = os.environ.get(key)
    if raw is None or raw.strip() == "":
        return list(default)
    return [part.strip() for part in raw.split(",") if part.strip()]


@dataclass(frozen=True)
class Settings:
    # --- Database secrets ---
    db_username: str
    db_password: str
    db_hostname: str
    db_port: int
    db_name: str
    db_engine: str
    sqlite_db_path: str

    # --- Auth / JWT ---
    jwt_secret_key: str

    # --- Logging & API ---
    log_file_path: str
    api_base_url: str
    log_level: str

    # --- EDA feature names ---
    feature_names: list[str]
    target_column: str
    processed_data_path: str
    model_path: str

    # --- Model training hyperparameters ---
    ml_n_estimators: int
    ml_max_depth: int | None
    ml_random_state: int
    ml_test_size: float
    ml_epochs: int

    # --- Experiment metadata ---
    experiment_name: str
    experiment_version: str
    expected_accuracy: float

    def database_url(self) -> str:
        """Build SQLAlchemy URL from secrets. Defaults to SQLite for local/demo."""
        engine = self.db_engine.lower().strip()
        if engine in {"sqlite", "sqlite3"}:
            return f"sqlite:///{self.sqlite_db_path}"
        # PostgreSQL-style connection using DB_* secrets
        user = self.db_username
        password = self.db_password
        host = self.db_hostname
        port = self.db_port
        name = self.db_name
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"

    def safe_summary(self) -> dict:
        """Non-secret summary suitable for logs and /health."""
        return {
            "db_engine": self.db_engine,
            "db_hostname": self.db_hostname,
            "db_port": self.db_port,
            "db_name": self.db_name,
            "db_username": self.db_username,
            "feature_names": self.feature_names,
            "target_column": self.target_column,
            "ml_n_estimators": self.ml_n_estimators,
            "ml_max_depth": self.ml_max_depth,
            "ml_epochs": self.ml_epochs,
            "ml_random_state": self.ml_random_state,
            "ml_test_size": self.ml_test_size,
            "expected_accuracy": self.expected_accuracy,
            "experiment_name": self.experiment_name,
            "experiment_version": self.experiment_version,
        }


@lru_cache
def get_settings() -> Settings:
    max_depth_raw = os.environ.get("ML_MAX_DEPTH", "").strip()
    max_depth = int(max_depth_raw) if max_depth_raw else None

    return Settings(
        db_username=_get("DB_USERNAME", "receptionist"),
        db_password=_get("DB_PASSWORD", "changeme"),
        db_hostname=_get("DB_HOSTNAME", "localhost"),
        db_port=_get_int("DB_PORT", 5432),
        db_name=_get("DB_NAME", "ai_receptionist"),
        db_engine=_get("DB_ENGINE", "sqlite"),
        sqlite_db_path=_get("SQLITE_DB_PATH", "./data/receptionist.db"),
        jwt_secret_key=_get("JWT_SECRET_KEY", "dev-secret-change-in-production"),
        log_file_path=_get("LOG_FILE_PATH", "logs/app.log"),
        api_base_url=_get("API_BASE_URL", "http://127.0.0.1:8000"),
        log_level=_get("LOG_LEVEL", "INFO"),
        feature_names=_get_list(
            "FEATURE_NAMES",
            [
                "Age",
                "WaitingDays",
                "AppointmentWeekday",
                "AppointmentHour",
                "SMS_received",
            ],
        ),
        target_column=_get("TARGET_COLUMN", "No-show"),
        processed_data_path=_get(
            "PROCESSED_DATA_PATH",
            "data/processed/processed_appointments.csv",
        ),
        model_path=_get("MODEL_PATH", "data/model/no_show_model.pkl"),
        ml_n_estimators=_get_int("ML_N_ESTIMATORS", 100),
        ml_max_depth=max_depth,
        ml_random_state=_get_int("ML_RANDOM_STATE", 42),
        ml_test_size=_get_float("ML_TEST_SIZE", 0.2),
        ml_epochs=_get_int("ML_EPOCHS", 10),
        experiment_name=_get("EXPERIMENT_NAME", "appointment-no-show"),
        experiment_version=_get("EXPERIMENT_VERSION", "1.0.0"),
        expected_accuracy=_get_float("EXPECTED_ACCURACY", 0.75),
    )
