import os


class Config:
    _db_url = os.getenv("DATABASE_URL", "sqlite:///pulse_check.db")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SCHEDULER_CHECK_INTERVAL = int(os.getenv("SCHEDULER_CHECK_INTERVAL", "5"))
    ALERT_REPEAT_INTERVAL = int(os.getenv("ALERT_REPEAT_INTERVAL", "300"))