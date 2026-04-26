from datetime import datetime, timezone

from app.models import db


def _utcnow():
    # naive UTC — SQLite strips tzinfo anyway so we stay consistent
    return datetime.now(timezone.utc).replace(tzinfo=None)


class MonitorStatus:
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DOWN = "DOWN"


class Monitor(db.Model):
    """Tracks a single device via periodic heartbeat signals."""

    __tablename__ = "monitors"

    id = db.Column(db.String(128), primary_key=True)
    timeout = db.Column(db.Integer, nullable=False)
    alert_email = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(16), nullable=False, default=MonitorStatus.ACTIVE)
    deadline = db.Column(db.DateTime, nullable=True)
    last_heartbeat = db.Column(db.DateTime, nullable=True)
    last_alert_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow)

    def to_dict(self):
        remaining = None
        if self.deadline and self.status == MonitorStatus.ACTIVE:
            delta = self.deadline - _utcnow()
            remaining = max(0, int(delta.total_seconds()))

        return {
            "id": self.id,
            "timeout": self.timeout,
            "alert_email": self.alert_email,
            "status": self.status,
            "deadline": self.deadline.isoformat() + "Z" if self.deadline else None,
            "last_heartbeat": self.last_heartbeat.isoformat() + "Z" if self.last_heartbeat else None,
            "last_alert_at": self.last_alert_at.isoformat() + "Z" if self.last_alert_at else None,
            "time_remaining_seconds": remaining,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
        }
