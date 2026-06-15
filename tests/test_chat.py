from pathlib import Path
from unittest.mock import patch

import joblib
from fastapi.testclient import TestClient

from app.services import faq_classifier
from training.train_faq_classifier import train

BIZ_URL = "/api/businesses"
CHAT_URL = "/api/businesses/{business_id}/chat"

SAMPLE_BUSINESS = {
    "name": "Bella Hair Studio",
    "description": "A full-service hair salon.",
    "phone": "519-555-0101",
    "email": "info@bella.com",
    "address": "123 Main St, Waterloo, ON",
    "business_hours": "Mon-Fri 9am-6pm",
    "website": "https://bella.com",
    "is_active": True,
}

SAMPLE_FAQ = {
    "question": "What are your business hours?",
    "answer": "We are open Monday to Friday, 9 AM to 6 PM.",
    "category": "hours",
    "tags": ["hours", "general"],
    "is_active": True,
}


def _create_business(client: TestClient, auth_headers: dict) -> dict:
    resp = client.post(f"{BIZ_URL}/", json=SAMPLE_BUSINESS, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()


def _create_faq(client: TestClient, auth_headers: dict, business_id: int) -> dict:
    resp = client.post(
        f"{BIZ_URL}/{business_id}/faqs/",
        json=SAMPLE_FAQ,
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()


class TestTraining:
    def test_training_produces_working_model(self, tmp_path: Path):
        csv_path = Path(__file__).resolve().parent.parent / "data-collection" / "faq_training_data.csv"
        model_path = tmp_path / "faq_classifier.joblib"

        train(csv_path, model_path)

        pipeline = joblib.load(model_path)
        prediction = pipeline.predict(["what time do you open"])[0]
        assert prediction == "hours"


class TestChatEndpoint:
    def test_chat_endpoint_returns_answer(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        _create_faq(client, auth_headers, biz["id"])

        with patch.object(faq_classifier, "predict", return_value=("hours", 0.95)):
            resp = client.post(
                CHAT_URL.format(business_id=biz["id"]) + "/",
                json={"message": "when are you open"},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["fallback"] is False
        assert data["category"] == "hours"
        assert data["confidence"] == 0.95
        assert data["answer"] == SAMPLE_FAQ["answer"]
        assert data["matched_question"] == SAMPLE_FAQ["question"]

    def test_chat_low_confidence_returns_fallback(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        _create_faq(client, auth_headers, biz["id"])

        with patch.object(faq_classifier, "predict", return_value=("hours", 0.10)):
            resp = client.post(
                CHAT_URL.format(business_id=biz["id"]) + "/",
                json={"message": "random gibberish xyz"},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["fallback"] is True
        assert "not sure" in data["answer"].lower()

    def test_chat_nonexistent_business_returns_404(self, client, auth_headers):
        with patch.object(faq_classifier, "predict", return_value=("hours", 0.95)):
            resp = client.post(
                CHAT_URL.format(business_id=9999) + "/",
                json={"message": "what are your hours"},
                headers=auth_headers,
            )

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Business not found"

    def test_chat_missing_model_returns_fallback(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        _create_faq(client, auth_headers, biz["id"])

        faq_classifier.reset_cache()
        with patch.object(faq_classifier, "_model_path", return_value=Path("/nonexistent/model.joblib")):
            resp = client.post(
                CHAT_URL.format(business_id=biz["id"]) + "/",
                json={"message": "what are your hours"},
                headers=auth_headers,
            )

        faq_classifier.reset_cache()
        assert resp.status_code == 200
        data = resp.json()
        assert data["fallback"] is True
        assert data["category"] is None
        assert data["confidence"] == 0.0
