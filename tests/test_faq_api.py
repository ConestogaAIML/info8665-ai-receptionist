# ============================================================
# FAQ API Unit Tests
# INFO8665 - AI Receptionist
# Task 74 [UNITTEST][API]
# Author: Haibo Yuan
# ============================================================

import time

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


def _create_business(client: TestClient, auth_headers: dict) -> dict:
    response = client.post(f"{BIZ_URL}/", json=SAMPLE_BUSINESS, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


def _faqs_url(business_id: int) -> str:
    return f"{BIZ_URL}/{business_id}/faqs"


def create_sample_faq(client: TestClient, auth_headers: dict) -> dict:
    business = _create_business(client, auth_headers)
    payload = {
        "question": "What are your business hours?",
        "answer": "We are open Monday to Friday, 9 AM to 5 PM.",
        "category": "hours",
        "tags": ["hours", "general"],
        "is_active": True,
    }

    response = client.post(f"{_faqs_url(business['id'])}/", json=payload, headers=auth_headers)
    assert response.status_code == 201

    return response.json()


def test_create_faq_item_success(client, auth_headers):
    """
    Test creating a FAQ item successfully.
    测试：成功创建 FAQ。
    """
    business = _create_business(client, auth_headers)

    payload = {
        "question": "What are your business hours?",
        "answer": "We are open Monday to Friday, 9 AM to 5 PM.",
        "category": "hours",
        "tags": ["hours", "general"],
        "is_active": True,
    }

    response = client.post(f"{_faqs_url(business['id'])}/", json=payload, headers=auth_headers)

    assert response.status_code == 201

    data = response.json()
    assert data["question"] == payload["question"]
    assert data["answer"] == payload["answer"]
    assert data["tags"] == payload["tags"]
    assert data["is_active"] is True


def test_list_faq_items_success(client, auth_headers):
    """
    Test listing FAQ items successfully.
    测试：成功获取 FAQ 列表。
    """
    faq = create_sample_faq(client, auth_headers)

    response = client.get(f"{_faqs_url(faq['business_id'])}/", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert "count" in data
    assert "results" in data
    assert data["count"] >= 1
    assert isinstance(data["results"], list)


def test_get_faq_item_by_id_success(client, auth_headers):
    """
    Test getting a FAQ item by ID.
    测试：根据 ID 获取单个 FAQ。
    """
    faq = create_sample_faq(client, auth_headers)

    response = client.get(
        f"{_faqs_url(faq['business_id'])}/{faq['id']}/",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == faq["id"]
    assert data["question"] == faq["question"]
    assert data["answer"] == faq["answer"]


def test_update_faq_item_success(client, auth_headers):
    """
    Test updating a FAQ item successfully.
    测试：成功更新 FAQ。
    """
    faq = create_sample_faq(client, auth_headers)

    update_payload = {
        "question": "What is your updated schedule?",
        "answer": "We are open from 10 AM to 6 PM.",
        "category": "hours",
        "tags": ["schedule", "updated"],
        "is_active": True,
    }

    response = client.put(
        f"{_faqs_url(faq['business_id'])}/{faq['id']}/",
        json=update_payload,
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == faq["id"]
    assert data["question"] == update_payload["question"]
    assert data["answer"] == update_payload["answer"]
    assert data["tags"] == update_payload["tags"]
    assert data["is_active"] is True


def test_delete_faq_item_success(client, auth_headers):
    """
    Test deleting a FAQ item successfully.
    测试：成功删除 FAQ。
    """
    faq = create_sample_faq(client, auth_headers)

    response = client.delete(
        f"{_faqs_url(faq['business_id'])}/{faq['id']}/",
        headers=auth_headers,
    )

    assert response.status_code == 204


def test_get_non_existing_faq_returns_404(client, auth_headers):
    """
    Test getting a non-existing FAQ item.
    测试：查询不存在的 FAQ，应该返回 404。
    """
    business = _create_business(client, auth_headers)

    response = client.get(f"{_faqs_url(business['id'])}/999999/", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "FAQ not found"


def test_faq_api_requires_authentication(client, auth_headers):
    """
    Test FAQ API authentication requirement.
    测试：未登录访问 FAQ API 应该失败。
    """
    business = _create_business(client, auth_headers)
    response = client.get(f"{_faqs_url(business['id'])}/")

    assert response.status_code in [401, 403]


def test_faq_list_response_time_under_three_seconds(client, auth_headers):
    """
    Test FAQ list API response time.
    测试：FAQ 列表接口响应时间应小于 3 秒。
    """
    faq = create_sample_faq(client, auth_headers)

    start_time = time.time()
    response = client.get(f"{_faqs_url(faq['business_id'])}/", headers=auth_headers)
    end_time = time.time()

    assert response.status_code == 200
    assert (end_time - start_time) < 3
