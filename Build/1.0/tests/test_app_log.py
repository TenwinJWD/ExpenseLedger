import logging
import sys

from app.core import app_log, paths


def test_unhandled_error_is_written_to_the_log(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    saved = (sys.excepthook, list(app_log._logger.handlers))
    app_log._logger.handlers.clear()
    try:
        app_log.setup()
        try:
            raise ValueError("boom")
        except ValueError:
            monkeypatch.setattr(sys, "__excepthook__", lambda *a: None)
            app_log._on_error(*sys.exc_info())
        for h in app_log._logger.handlers:
            h.flush()
        text = paths.log_file().read_text(encoding="utf-8")
        assert "Unhandled error" in text and "ValueError: boom" in text
        assert text[2] == "-" and text[6] == "-"  # DD-Mon-YYYY
    finally:
        for h in app_log._logger.handlers:
            h.close()
        app_log._logger.handlers[:] = saved[1]
        sys.excepthook = saved[0]
