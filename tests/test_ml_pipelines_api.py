"""API tests for Assignment 6 ML Ops pipeline services."""

from pathlib import Path


def test_faq_pipeline_stages(client, auth_headers):
    collect = client.post(
        "/api/ml/faq/collect",
        json={"source": "local"},
        headers=auth_headers,
    )
    assert collect.status_code == 200, collect.text
    assert collect.json()["status"] == "ok"

    eda = client.get("/api/ml/faq/eda", headers=auth_headers)
    assert eda.status_code == 200, eda.text
    assert eda.json()["row_count"] > 0

    prep = client.post("/api/ml/faq/preprocess", json={}, headers=auth_headers)
    assert prep.status_code == 200, prep.text

    train = client.post("/api/ml/faq/train", json={}, headers=auth_headers)
    assert train.status_code == 200, train.text
    assert train.json()["accuracy"] >= 0.0

    validate = client.post("/api/ml/faq/validate", json={}, headers=auth_headers)
    assert validate.status_code == 200, validate.text
    assert "met_expectation" in validate.json()

    reload_resp = client.post("/api/ml/faq/reload", headers=auth_headers)
    assert reload_resp.status_code == 200, reload_resp.text
    assert reload_resp.json()["loaded"] is True


def test_appointment_pipeline_eda_and_validate(client, auth_headers):
    # Prefer processed artifact already in repo; preprocess if raw is present.
    raw = Path("data/raw/appointments.csv")
    if raw.exists():
        prep = client.post(
            "/api/ml/appointments/preprocess",
            json={"raw_path": str(raw)},
            headers=auth_headers,
        )
        assert prep.status_code == 200, prep.text

    eda = client.get("/api/ml/appointments/eda", headers=auth_headers)
    assert eda.status_code == 200, eda.text
    body = eda.json()
    assert body["stage"] == "eda"
    assert "feature_names" in body

    if Path("data/processed/processed_appointments.csv").exists() and Path(
        "data/model/no_show_model.pkl"
    ).exists():
        validate = client.post("/api/ml/appointments/validate", headers=auth_headers)
        assert validate.status_code == 200, validate.text
        assert "accuracy" in validate.json()

    reload_resp = client.post("/api/ml/appointments/reload", headers=auth_headers)
    assert reload_resp.status_code == 200, reload_resp.text
