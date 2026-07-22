from pathlib import Path

from app.config import get_settings


def test_public_config_summary_hides_database_credentials(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("DB_USERNAME", "private-user")
    monkeypatch.setenv("DB_PASSWORD", "private-password")

    summary = get_settings().safe_summary()

    assert "db_username" not in summary
    assert "db_password" not in summary
    assert "private-user" not in str(summary)
    assert "private-password" not in str(summary)

    get_settings.cache_clear()


def test_dockerfile_does_not_copy_missing_optional_data_directories():
    root = Path(__file__).resolve().parents[1]
    dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")
    dockerignore = (root / ".dockerignore").read_text(encoding="utf-8")

    assert "COPY data/model/" not in dockerfile
    assert "COPY data/processed/" not in dockerfile
    assert "!.env.example" in dockerignore
    assert ".venv-a5" in dockerignore
