import pytest
from fastapi.testclient import TestClient

BASE_URL = "/api/businesses"

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


def _create_business(client: TestClient, auth_headers: dict, overrides: dict = None) -> dict:
    payload = {**SAMPLE_BUSINESS, **(overrides or {})}
    resp = client.post(f"{BASE_URL}/", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()


class TestCreateBusiness:
    def test_create_business_returns_201(self, client, auth_headers):
        resp = client.post(f"{BASE_URL}/", json=SAMPLE_BUSINESS, headers=auth_headers)
        assert resp.status_code == 201

    def test_create_business_returns_correct_fields(self, client, auth_headers):
        data = _create_business(client, auth_headers)
        assert data["name"] == SAMPLE_BUSINESS["name"]
        assert data["email"] == SAMPLE_BUSINESS["email"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_business_requires_auth(self, client):
        resp = client.post(f"{BASE_URL}/", json=SAMPLE_BUSINESS)
        assert resp.status_code in (401, 403)

    def test_create_business_requires_name(self, client, auth_headers):
        payload = {k: v for k, v in SAMPLE_BUSINESS.items() if k != "name"}
        resp = client.post(f"{BASE_URL}/", json=payload, headers=auth_headers)
        assert resp.status_code == 422


class TestListBusinesses:
    def test_list_returns_empty_initially(self, client, auth_headers):
        resp = client.get(f"{BASE_URL}/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == {"count": 0, "results": []}

    def test_list_returns_all_businesses(self, client, auth_headers):
        _create_business(client, auth_headers, {"name": "Shop A"})
        _create_business(client, auth_headers, {"name": "Shop B"})
        resp = client.get(f"{BASE_URL}/", headers=auth_headers)
        data = resp.json()
        assert data["count"] == 2

    def test_list_filter_by_active(self, client, auth_headers):
        _create_business(client, auth_headers, {"name": "Active Shop", "is_active": True})
        _create_business(client, auth_headers, {"name": "Inactive Shop", "is_active": False})
        resp = client.get(f"{BASE_URL}/?is_active=true", headers=auth_headers)
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["name"] == "Active Shop"


class TestGetBusiness:
    def test_get_existing_business(self, client, auth_headers):
        created = _create_business(client, auth_headers)
        resp = client.get(f"{BASE_URL}/{created['id']}/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_get_nonexistent_business_returns_404(self, client, auth_headers):
        resp = client.get(f"{BASE_URL}/9999/", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Business not found"


class TestUpdateBusiness:
    def test_update_business_changes_fields(self, client, auth_headers):
        created = _create_business(client, auth_headers)
        updated_payload = {**SAMPLE_BUSINESS, "name": "Updated Studio", "phone": "519-999-0000"}
        resp = client.put(f"{BASE_URL}/{created['id']}/", json=updated_payload, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Studio"
        assert data["phone"] == "519-999-0000"

    def test_update_nonexistent_business_returns_404(self, client, auth_headers):
        resp = client.put(f"{BASE_URL}/9999/", json=SAMPLE_BUSINESS, headers=auth_headers)
        assert resp.status_code == 404


class TestDeleteBusiness:
    def test_delete_business_returns_204(self, client, auth_headers):
        created = _create_business(client, auth_headers)
        resp = client.delete(f"{BASE_URL}/{created['id']}/", headers=auth_headers)
        assert resp.status_code == 204

    def test_deleted_business_is_not_found(self, client, auth_headers):
        created = _create_business(client, auth_headers)
        client.delete(f"{BASE_URL}/{created['id']}/", headers=auth_headers)
        resp = client.get(f"{BASE_URL}/{created['id']}/", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_nonexistent_business_returns_404(self, client, auth_headers):
        resp = client.delete(f"{BASE_URL}/9999/", headers=auth_headers)
        assert resp.status_code == 404
