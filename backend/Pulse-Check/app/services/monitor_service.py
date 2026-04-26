import json
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

    @staticmethod
    def heartbeat(device_id):
        monitor = db.session.get(Monitor, device_id)
        if not monitor:
            return None

        now = _utcnow()
        monitor.status = MonitorStatus.ACTIVE
        monitor.deadline = now + timedelta(seconds=monitor.timeout)
        monitor.last_heartbeat = now
        monitor.updated_at = now

        db.session.commit()
        return monitor

    @staticmethod
    def check_expired_monitors(alert_repeat_interval):
        now = _utcnow()

        newly_expired = Monitor.query.filter(
            Monitor.status == MonitorStatus.ACTIVE,
            Monitor.deadline <= now,
        ).all()

        for monitor in newly_expired:
            monitor.status = MonitorStatus.DOWN
            monitor.deadline = None
            monitor.updated_at = now

            print(json.dumps({
                "ALERT": f"Device {monitor.id} is down!",
                "device_id": monitor.id,
                "alert_email": monitor.alert_email,
                "time": now.isoformat() + "Z",
                "alert_type": "initial",
            }))

        if newly_expired:
            db.session.commit()

    @staticmethod
    def pause(device_id):
        monitor = db.session.get(Monitor, device_id)
        if not monitor:
            return None

        if monitor.status == MonitorStatus.DOWN:
            raise ValueError("Cannot pause a DOWN monitor — send a heartbeat first.")

        if monitor.status == MonitorStatus.PAUSED:
            return monitor  # already paused, no-op

        now = _utcnow()
        monitor.status = MonitorStatus.PAUSED
        monitor.deadline = None
        monitor.updated_at = now
        db.session.commit()
        return monitor