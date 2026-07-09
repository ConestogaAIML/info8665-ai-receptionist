import importlib


def test_configure_application_logging_writes_info_with_assignment_formatter(tmp_path, monkeypatch):
    log_file = tmp_path / "app.log"
    monkeypatch.setenv("LOG_FILE_PATH", str(log_file))

    logging_config = importlib.import_module("app.logging_config")
    logger = logging_config.configure_application_logging()
    logger.info("assignment logging smoke test")

    for handler in logger.handlers:
        handler.flush()

    contents = log_file.read_text(encoding="utf-8")

    assert "ai_receptionist - INFO - assignment logging smoke test" in contents
    assert " - " in contents
    assert len(contents.split(" - ")) >= 4

