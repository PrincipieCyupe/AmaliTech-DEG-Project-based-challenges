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
    def get_monitor(device_id):
        return db.session.get(Monitor, device_id)

    @staticmethod
    def list_monitors(status_filter=None):
        query = Monitor.query

        if status_filter:
            normalized = status_filter.upper()
            valid = {MonitorStatus.ACTIVE, MonitorStatus.PAUSED, MonitorStatus.DOWN}
            if normalized not in valid:
                raise ValueError(
                    f"Invalid status '{status_filter}'. Use: {', '.join(sorted(valid))}"
                )
            query = query.filter(Monitor.status == normalized)

        return query.order_by(Monitor.created_at.desc()).all()

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
        monitor.last_alert_at = None  # device is alive, stop re-alerting

        db.session.commit()
        return monitor

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

    @staticmethod
    def check_expired_monitors(alert_repeat_interval):
        now = _utcnow()

        # pass 1: catch newly expired monitors
        newly_expired = Monitor.query.filter(
            Monitor.status == MonitorStatus.ACTIVE,
            Monitor.deadline <= now,
        ).all()

        for monitor in newly_expired:
            monitor.status = MonitorStatus.DOWN
            monitor.deadline = None
            monitor.last_alert_at = now
            monitor.updated_at = now

            print(json.dumps({
                "ALERT": f"Device {monitor.id} is down!",
                "device_id": monitor.id,
                "alert_email": monitor.alert_email,
                "time": now.isoformat() + "Z",
                "alert_type": "initial",
            }))

        # pass 2: re-alert devices that are still down past the cooldown
        repeat_cutoff = now - timedelta(seconds=alert_repeat_interval)

        still_down = Monitor.query.filter(
            Monitor.status == MonitorStatus.DOWN,
            Monitor.last_alert_at <= repeat_cutoff,
        ).all()

        for monitor in still_down:
            monitor.last_alert_at = now
            monitor.updated_at = now

            print(json.dumps({
                "ALERT": f"Device {monitor.id} is still down!",
                "device_id": monitor.id,
                "alert_email": monitor.alert_email,
                "time": now.isoformat() + "Z",
                "alert_type": "repeated",
            }))

        if newly_expired or still_down:
            db.session.commit()