"""ML Ops pipeline API services for FAQ and appointment no-show use cases."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.config import get_settings
from app.database import get_db
from app.logging_config import configure_application_logging
from app.services import faq_ml_pipeline
from app.services.appointment_prediction_service import reset_model_cache
from app.services.evaluate_model import evaluate_no_show_model
from app.services.preprocess_data import preprocess_appointments
from app.services.train_model import train_no_show_model

logger = configure_application_logging()

router = APIRouter(
    prefix="/api/ml",
    tags=["ML Ops Pipelines"],
    dependencies=[Depends(verify_token)],
)


class FaqCollectRequest(BaseModel):
    source: str = Field(default="local", description="local | db")


class FaqPathRequest(BaseModel):
    csv_path: str | None = None


class AppointmentPreprocessRequest(BaseModel):
    raw_path: str = "data/raw/appointments.csv"


# ---------------------------------------------------------------------------
# FAQ chatbot ML Ops pipelines
# ---------------------------------------------------------------------------


@router.post("/faq/collect", summary="FAQ data collection pipeline")
def faq_collect(payload: FaqCollectRequest):
    logger.info("API START POST /api/ml/faq/collect source=%s", payload.source)
    try:
        result = faq_ml_pipeline.collect_faq_training_data(source=payload.source)
    except Exception as exc:  # noqa: BLE001
        logger.exception("API FAIL POST /api/ml/faq/collect")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info("API END POST /api/ml/faq/collect status=%s", result.get("status"))
    return result


@router.get("/faq/eda", summary="FAQ exploratory data analysis pipeline")
def faq_eda(csv_path: str | None = None):
    logger.info("API START GET /api/ml/faq/eda")
    try:
        result = faq_ml_pipeline.eda_faq_dataset(csv_path=csv_path)
    except Exception as exc:  # noqa: BLE001
        logger.exception("API FAIL GET /api/ml/faq/eda")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info("API END GET /api/ml/faq/eda rows=%s", result.get("row_count"))
    return result


@router.post("/faq/preprocess", summary="FAQ preprocessing pipeline")
def faq_preprocess(payload: FaqPathRequest | None = None):
    logger.info("API START POST /api/ml/faq/preprocess")
    try:
        result = faq_ml_pipeline.preprocess_faq_dataset(
            csv_path=payload.csv_path if payload else None
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("API FAIL POST /api/ml/faq/preprocess")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info("API END POST /api/ml/faq/preprocess rows_after=%s", result.get("rows_after"))
    return result


@router.post("/faq/train", summary="FAQ model training pipeline")
def faq_train(payload: FaqPathRequest | None = None):
    logger.info("API START POST /api/ml/faq/train")
    try:
        result = faq_ml_pipeline.train_faq_model(
            csv_path=payload.csv_path if payload else None
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("API FAIL POST /api/ml/faq/train")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info("API END POST /api/ml/faq/train accuracy=%s", result.get("accuracy"))
    return result


@router.post("/faq/validate", summary="FAQ model validation pipeline")
def faq_validate(payload: FaqPathRequest | None = None):
    logger.info("API START POST /api/ml/faq/validate")
    try:
        result = faq_ml_pipeline.validate_faq_model(
            csv_path=payload.csv_path if payload else None
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("API FAIL POST /api/ml/faq/validate")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    logger.info(
        "API END POST /api/ml/faq/validate accuracy=%s met=%s",
        result.get("accuracy"),
        result.get("met_expectation"),
    )
    return result


@router.post("/faq/reload", summary="Reload FAQ model into serving cache")
def faq_reload():
    logger.info("API START POST /api/ml/faq/reload")
    result = faq_ml_pipeline.reload_faq_model()
    logger.info("API END POST /api/ml/faq/reload loaded=%s", result.get("loaded"))
    return result


# ---------------------------------------------------------------------------
# Appointment no-show ML Ops pipelines
# ---------------------------------------------------------------------------


@router.post("/appointments/preprocess", summary="Appointment preprocess + EDA pipeline")
def appointments_preprocess(payload: AppointmentPreprocessRequest | None = None):
    logger.info("API START POST /api/ml/appointments/preprocess")
    raw_path = payload.raw_path if payload else "data/raw/appointments.csv"
    try:
        out = preprocess_appointments(raw_path=raw_path)
    except Exception as exc:  # noqa: BLE001
        logger.exception("API FAIL POST /api/ml/appointments/preprocess")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result = {
        "stage": "preprocess",
        "raw_path": raw_path,
        "processed_path": str(out),
        "status": "ok",
    }
    logger.info("API END POST /api/ml/appointments/preprocess path=%s", out)
    return result


@router.get("/appointments/eda", summary="Appointment EDA summary from secrets + data")
def appointments_eda():
    logger.info("API START GET /api/ml/appointments/eda")
    settings = get_settings()
    processed = Path(settings.processed_data_path)
    raw = Path("data/raw/appointments.csv")
    summary: dict = {
        "stage": "eda",
        "experiment_name": settings.experiment_name,
        "experiment_version": settings.experiment_version,
        "feature_names": settings.feature_names,
        "target_column": settings.target_column,
        "raw_exists": raw.exists(),
        "processed_exists": processed.exists(),
        "status": "ok",
    }
    if processed.exists():
        import pandas as pd

        df = pd.read_csv(processed)
        summary["processed_rows"] = int(len(df))
        summary["processed_columns"] = list(df.columns)
        if settings.target_column in df.columns:
            summary["target_rate"] = float(df[settings.target_column].mean())
    if raw.exists():
        summary["raw_rows"] = sum(1 for _ in raw.open(encoding="utf-8")) - 1
    logger.info(
        "API END GET /api/ml/appointments/eda processed_rows=%s",
        summary.get("processed_rows"),
    )
    return summary


@router.post("/appointments/train", summary="Appointment no-show training pipeline")
def appointments_train():
    logger.info("API START POST /api/ml/appointments/train")
    try:
        result = train_no_show_model()
        reset_model_cache()
    except Exception as exc:  # noqa: BLE001
        logger.exception("API FAIL POST /api/ml/appointments/train")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result = {**result, "stage": "train", "status": "ok"}
    logger.info(
        "API END POST /api/ml/appointments/train accuracy=%s",
        result.get("accuracy"),
    )
    return result


@router.post("/appointments/validate", summary="Appointment model validation pipeline")
def appointments_validate():
    logger.info("API START POST /api/ml/appointments/validate")
    try:
        result = evaluate_no_show_model()
    except Exception as exc:  # noqa: BLE001
        logger.exception("API FAIL POST /api/ml/appointments/validate")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result = {**result, "stage": "validate", "status": "ok"}
    logger.info(
        "API END POST /api/ml/appointments/validate accuracy=%s met=%s",
        result.get("accuracy"),
        result.get("met_expectation"),
    )
    return result


@router.post("/appointments/reload", summary="Reload no-show model into serving cache")
def appointments_reload():
    logger.info("API START POST /api/ml/appointments/reload")
    reset_model_cache()
    settings = get_settings()
    exists = Path(settings.model_path).exists()
    result = {
        "stage": "reload",
        "model_path": settings.model_path,
        "exists": exists,
        "status": "ok" if exists else "missing_model",
    }
    logger.info("API END POST /api/ml/appointments/reload exists=%s", exists)
    return result


@router.post(
    "/appointments/run-full",
    summary="Run preprocess → train → validate for appointments",
)
def appointments_run_full(
    payload: AppointmentPreprocessRequest | None = None,
    db: Session = Depends(get_db),  # noqa: ARG001 — keeps auth+db consistent
):
    logger.info("API START POST /api/ml/appointments/run-full")
    try:
        raw_path = payload.raw_path if payload else "data/raw/appointments.csv"
        processed = preprocess_appointments(raw_path=raw_path)
        train_result = train_no_show_model()
        reset_model_cache()
        validate_result = evaluate_no_show_model()
    except Exception as exc:  # noqa: BLE001
        logger.exception("API FAIL POST /api/ml/appointments/run-full")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result = {
        "stage": "full_pipeline",
        "processed_path": str(processed),
        "train": train_result,
        "validate": validate_result,
        "status": "ok",
    }
    logger.info("API END POST /api/ml/appointments/run-full status=ok")
    return result
