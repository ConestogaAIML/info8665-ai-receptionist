# ============================================================
# FAQ API Unit Tests
# INFO8665 - AI Receptionist
# Task 74 [UNITTEST][API]
# Author: Haibo Yuan
# ============================================================

import os
import sys
import time

# Add project root path so pytest can import app.main correctly
# 项目根目录加入 Python 搜索路径，解决 No module named 'app'
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from fastapi.testclient import TestClient
from app.main import app

# Create FastAPI test client
# 创建 FastAPI 测试客户端
client = TestClient(app)


def get_auth_headers():
    """
    Get JWT token for protected API endpoints.
    获取 JWT token，因为 /api/faq/ 需要认证。
    """
    response = client.post("/auth/token?business_id=1")
    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_sample_faq(headers):
    """
    Helper function to create one sample FAQ item.
    辅助函数：创建一个测试用 FAQ。
    """
    payload = {
        "question": "What are your business hours?",
        "answer": "We are open Monday to Friday, 9 AM to 5 PM.",
        "tags": ["hours", "general"],
        "is_active": True,
    }

    response = client.post("/api/faq/", json=payload, headers=headers)
    assert response.status_code == 201

    return response.json()


def test_create_faq_item_success():
    """
    Test creating a FAQ item successfully.
    测试：成功创建 FAQ。
    """
    headers = get_auth_headers()

    payload = {
        "question": "What are your business hours?",
        "answer": "We are open Monday to Friday, 9 AM to 5 PM.",
        "tags": ["hours", "general"],
        "is_active": True,
    }

    response = client.post("/api/faq/", json=payload, headers=headers)

    assert response.status_code == 201

    data = response.json()
    assert data["question"] == payload["question"]
    assert data["answer"] == payload["answer"]
    assert data["tags"] == payload["tags"]
    assert data["is_active"] is True


def test_list_faq_items_success():
    """
    Test listing FAQ items successfully.
    测试：成功获取 FAQ 列表。
    """
    headers = get_auth_headers()
    create_sample_faq(headers)

    response = client.get("/api/faq/", headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert "count" in data
    assert "results" in data
    assert data["count"] >= 1
    assert isinstance(data["results"], list)


def test_get_faq_item_by_id_success():
    """
    Test getting a FAQ item by ID.
    测试：根据 ID 获取单个 FAQ。
    """
    headers = get_auth_headers()
    faq = create_sample_faq(headers)

    response = client.get(f"/api/faq/{faq['id']}/", headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == faq["id"]
    assert data["question"] == faq["question"]
    assert data["answer"] == faq["answer"]


def test_update_faq_item_success():
    """
    Test updating a FAQ item successfully.
    测试：成功更新 FAQ。
    """
    headers = get_auth_headers()
    faq = create_sample_faq(headers)

    update_payload = {
        "question": "What is your updated schedule?",
        "answer": "We are open from 10 AM to 6 PM.",
        "tags": ["schedule", "updated"],
        "is_active": True,
    }

    response = client.put(
        f"/api/faq/{faq['id']}/",
        json=update_payload,
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == faq["id"]
    assert data["question"] == update_payload["question"]
    assert data["answer"] == update_payload["answer"]
    assert data["tags"] == update_payload["tags"]
    assert data["is_active"] is True


def test_delete_faq_item_success():
    """
    Test deleting a FAQ item successfully.
    测试：成功删除 FAQ。
    """
    headers = get_auth_headers()
    faq = create_sample_faq(headers)

    response = client.delete(f"/api/faq/{faq['id']}/", headers=headers)

    assert response.status_code == 204


def test_get_non_existing_faq_returns_404():
    """
    Test getting a non-existing FAQ item.
    测试：查询不存在的 FAQ，应该返回 404。
    """
    headers = get_auth_headers()

    response = client.get("/api/faq/999999/", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "FAQ item not found"


def test_faq_api_requires_authentication():
    """
    Test FAQ API authentication requirement.
    测试：未登录访问 FAQ API 应该失败。
    """
    response = client.get("/api/faq/")

    assert response.status_code in [401, 403]


def test_faq_list_response_time_under_three_seconds():
    """
    Test FAQ list API response time.
    测试：FAQ 列表接口响应时间应小于 3 秒。
    """
    headers = get_auth_headers()

    start_time = time.time()
    response = client.get("/api/faq/", headers=headers)
    end_time = time.time()

    assert response.status_code == 200
    assert (end_time - start_time) < 3