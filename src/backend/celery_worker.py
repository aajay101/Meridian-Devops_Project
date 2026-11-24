from celery import Celery
from celery.schedules import crontab


def make_celery(flask_app):
    celery = Celery(
        flask_app.import_name,
        broker=flask_app.config["CELERY_BROKER_URL"],
        backend=flask_app.config["CELERY_RESULT_BACKEND"],
    )
    celery.conf.update(
        result_backend=flask_app.config["CELERY_RESULT_BACKEND"],
        timezone=flask_app.config.get("CELERY_TIMEZONE", "Asia/Kolkata"),
        enable_utc=True,
        # FIX 1 — Auto-expire task results after 1 hour to prevent Redis memory leak.
        result_expires=3600,
        # FIX 2 — Retry broker connection on startup instead of crashing immediately.
        broker_connection_retry_on_startup=True,
        # FIX 3 — Process one task at a time; avoids idle workers hoarding tasks.
        worker_prefetch_multiplier=1,
        # FIX 4 — Enforce JSON-only serialization for safety (no pickle/yaml).
        accept_content=["json"],
        task_serializer="json",
        result_serializer="json",
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


from app import create_app  # noqa: E402

flask_app = create_app()
celery = make_celery(flask_app)

celery.conf.beat_schedule = {
    "daily-reminders": {
        "task": "tasks.reminders.send_daily_reminders",
        "schedule": crontab(
            hour=flask_app.config.get("REMINDER_HOUR", 8),
            minute=flask_app.config.get("REMINDER_MINUTE", 0),
        ),
    },
    "monthly-report": {
        "task": "tasks.reports.send_monthly_report",
        "schedule": crontab(
            day_of_month="1",
            hour=flask_app.config.get("REPORT_HOUR", 6),
            minute=flask_app.config.get("REPORT_MINUTE", 0),
        ),
    },
}

from tasks import reminders, reports, exports  # noqa: E402, F401
