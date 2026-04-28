import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from zoneinfo import ZoneInfo


class TZFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz_name="Asia/Shanghai"):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.tz = ZoneInfo(tz_name)

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat(timespec="seconds")


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _resolve_log_dir(configured_dir: str) -> Path:
    """
    In Docker, prefer /var/log/diet. If permission is denied, fallback to /tmp/diet-logs.
    """
    primary = Path(configured_dir)
    try:
        primary.mkdir(parents=True, exist_ok=True)
        return primary
    except OSError:
        fallback = Path("/tmp/diet-logs")
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def configure_logging(app):
    level_name = str(app.config.get("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    tz_name = app.config.get("LOG_TIMEZONE", "Asia/Shanghai")
    to_file = _as_bool(app.config.get("LOG_TO_FILE", True), default=True)

    base_name = app.config.get("LOG_FILE_BASENAME", "diet-be")
    backup_count = int(app.config.get("LOG_BACKUP_COUNT", 14))
    log_dir = _resolve_log_dir(app.config.get("LOG_DIR", "/var/log/diet"))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    formatter = TZFormatter(fmt=fmt, tz_name=tz_name)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    if to_file:
        file_path = os.fspath(log_dir / f"{base_name}.log")
        file_handler = TimedRotatingFileHandler(
            filename=file_path,
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Keep common library logs aligned with root handlers/level
    logging.getLogger("werkzeug").setLevel(level)
    logging.getLogger("flask.app").setLevel(level)

    app.logger.info(
        "logging initialized level=%s timezone=%s log_dir=%s to_file=%s",
        level_name,
        tz_name,
        os.fspath(log_dir),
        to_file,
    )
