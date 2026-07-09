import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_recent_logs_endpoint_returns_visible_log_lines():
    app.state.logger.info("visible log endpoint smoke test")

    response = client.get("/logs/recent")

    assert response.status_code == 200
    data = response.json()
    assert "log_file" in data
    assert "lines" in data
    assert any("visible log endpoint smoke test" in line for line in data["lines"])

