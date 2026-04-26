import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///pulse_check.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # scheduler polls on this interval (seconds)
    SCHEDULER_CHECK_INTERVAL = int(os.getenv("SCHEDULER_CHECK_INTERVAL", "5"))