import pytest
from fastapi.testclient import TestClient

BIZ_URL = "/api/businesses"

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


def _faqs_url(business_id: int) -> str:
    return f"{BIZ_URL}/{business_id}/faqs"


def _create_faq(
    client: TestClient,
    auth_headers: dict,
    business_id: int,
    overrides: dict = None,
) -> dict:
    payload = {**SAMPLE_FAQ, **(overrides or {})}
    resp = client.post(f"{_faqs_url(business_id)}/", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()


class TestCreateFAQ:
    def test_create_faq_returns_201(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        resp = client.post(f"{_faqs_url(biz['id'])}/", json=SAMPLE_FAQ, headers=auth_headers)
        assert resp.status_code == 201

    def test_create_faq_has_correct_business_id(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        data = _create_faq(client, auth_headers, biz["id"])
        assert data["business_id"] == biz["id"]
        assert data["question"] == SAMPLE_FAQ["question"]
        assert data["category"] == SAMPLE_FAQ["category"]
        assert "hours" in data["tags"]

    def test_create_faq_for_nonexistent_business_returns_404(self, client, auth_headers):
        resp = client.post(f"{_faqs_url(9999)}/", json=SAMPLE_FAQ, headers=auth_headers)
        assert resp.status_code == 404

    def test_create_faq_requires_auth(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        resp = client.post(f"{_faqs_url(biz['id'])}/", json=SAMPLE_FAQ)
        assert resp.status_code in (401, 403)

    def test_create_faq_requires_question_and_answer(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        resp = client.post(f"{_faqs_url(biz['id'])}/", json={"category": "hours"}, headers=auth_headers)
        assert resp.status_code == 422


class TestListFAQs:
    def test_list_faqs_empty_initially(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        resp = client.get(f"{_faqs_url(biz['id'])}/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == {"count": 0, "results": []}

    def test_list_faqs_returns_all_for_business(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        _create_faq(client, auth_headers, biz["id"], {"question": "Q1?"})
        _create_faq(client, auth_headers, biz["id"], {"question": "Q2?"})
        resp = client.get(f"{_faqs_url(biz['id'])}/", headers=auth_headers)
        assert resp.json()["count"] == 2

    def test_list_faqs_isolated_per_business(self, client, auth_headers):
        biz1 = _create_business(client, auth_headers)
        biz2 = _create_business(client, auth_headers)
        _create_faq(client, auth_headers, biz1["id"])
        resp = client.get(f"{_faqs_url(biz2['id'])}/", headers=auth_headers)
        assert resp.json()["count"] == 0

    def test_list_faqs_filter_by_category(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        _create_faq(client, auth_headers, biz["id"], {"question": "Hours?", "category": "hours"})
        _create_faq(client, auth_headers, biz["id"], {"question": "Price?", "category": "pricing"})
        resp = client.get(f"{_faqs_url(biz['id'])}/?category=pricing", headers=auth_headers)
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["category"] == "pricing"

    def test_list_faqs_filter_by_is_active(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        _create_faq(client, auth_headers, biz["id"], {"question": "Active?", "is_active": True})
        _create_faq(client, auth_headers, biz["id"], {"question": "Inactive?", "is_active": False})
        resp = client.get(f"{_faqs_url(biz['id'])}/?is_active=false", headers=auth_headers)
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["is_active"] is False

    def test_list_faqs_for_nonexistent_business_returns_404(self, client, auth_headers):
        resp = client.get(f"{_faqs_url(9999)}/", headers=auth_headers)
        assert resp.status_code == 404


class TestGetFAQ:
    def test_get_existing_faq(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        created = _create_faq(client, auth_headers, biz["id"])
        resp = client.get(f"{_faqs_url(biz['id'])}/{created['id']}/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_get_nonexistent_faq_returns_404(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        resp = client.get(f"{_faqs_url(biz['id'])}/9999/", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.json()["detail"] == "FAQ not found"

    def test_get_faq_from_wrong_business_returns_404(self, client, auth_headers):
        biz1 = _create_business(client, auth_headers)
        biz2 = _create_business(client, auth_headers)
        faq = _create_faq(client, auth_headers, biz1["id"])
        resp = client.get(f"{_faqs_url(biz2['id'])}/{faq['id']}/", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateFAQ:
    def test_update_faq_changes_answer(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        created = _create_faq(client, auth_headers, biz["id"])
        updated_payload = {**SAMPLE_FAQ, "answer": "Updated answer.", "category": "general"}
        resp = client.put(
            f"{_faqs_url(biz['id'])}/{created['id']}/",
            json=updated_payload,
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["answer"] == "Updated answer."
        assert data["category"] == "general"

    def test_update_nonexistent_faq_returns_404(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        resp = client.put(
            f"{_faqs_url(biz['id'])}/9999/",
            json=SAMPLE_FAQ,
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestDeleteFAQ:
    def test_delete_faq_returns_204(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        created = _create_faq(client, auth_headers, biz["id"])
        resp = client.delete(f"{_faqs_url(biz['id'])}/{created['id']}/", headers=auth_headers)
        assert resp.status_code == 204

    def test_deleted_faq_is_not_found(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        created = _create_faq(client, auth_headers, biz["id"])
        client.delete(f"{_faqs_url(biz['id'])}/{created['id']}/", headers=auth_headers)
        resp = client.get(f"{_faqs_url(biz['id'])}/{created['id']}/", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_nonexistent_faq_returns_404(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        resp = client.delete(f"{_faqs_url(biz['id'])}/9999/", headers=auth_headers)
        assert resp.status_code == 404

    def test_deleting_business_cascades_to_faqs(self, client, auth_headers):
        biz = _create_business(client, auth_headers)
        faq = _create_faq(client, auth_headers, biz["id"])
        client.delete(f"{BIZ_URL}/{biz['id']}/", headers=auth_headers)
        # Business is gone; the nested route should 404 on the business check
        resp = client.get(f"{_faqs_url(biz['id'])}/{faq['id']}/", headers=auth_headers)
        assert resp.status_code == 404
