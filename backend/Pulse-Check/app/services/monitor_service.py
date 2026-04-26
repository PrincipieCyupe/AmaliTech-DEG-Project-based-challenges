from datetime import timedelta

from app.models import db
from app.models.monitor import Monitor, MonitorStatus, _utcnow


class MonitorService:

    @staticmethod
    def create_monitor(device_id, timeout, alert_email):
        existing = db.session.get(Monitor, device_id)
        if existing:
            raise ValueError(f"Monitor '{device_id}' already exists.")

        now = _utcnow()
        monitor = Monitor(
            id=device_id,
            timeout=timeout,
            alert_email=alert_email,
            status=MonitorStatus.ACTIVE,
            deadline=now + timedelta(seconds=timeout),
            created_at=now,
            updated_at=now,
        )
        db.session.add(monitor)
        db.session.commit()
        return monitor
