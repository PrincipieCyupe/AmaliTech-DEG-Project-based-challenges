from apscheduler.schedulers.background import BackgroundScheduler

from app.services.monitor_service import MonitorService

scheduler = BackgroundScheduler(daemon=True)


def _check_monitors(app, alert_repeat_interval):
    with app.app_context():
        MonitorService.check_expired_monitors(alert_repeat_interval)


def init_scheduler(app):
    if scheduler.running:
        return

    interval = app.config["SCHEDULER_CHECK_INTERVAL"]
    repeat_interval = app.config["ALERT_REPEAT_INTERVAL"]

    scheduler.add_job(
        func=_check_monitors,
        trigger="interval",
        seconds=interval,
        args=[app, repeat_interval],
        id="monitor_watchdog",
        replace_existing=True,
    )
    scheduler.start()
