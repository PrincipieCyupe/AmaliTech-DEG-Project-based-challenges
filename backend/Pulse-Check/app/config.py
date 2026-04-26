import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///pulse_check.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # scheduler polls on the interal of 5 seconds interval
    SCHEDULER_CHECK_INTERVAL = int(os.getenv("SCHEDULER_CHECK_INTERVAL", "5"))

    # how often to re-alert for monitors still down (300 seconds or 5 miutes)
    ALERT_REPEAT_INTERVAL = int(os.getenv("ALERT_REPEAT_INTERVAL", "300"))