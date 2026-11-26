
import os

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
        result_expires=3600,
        broker_connection_retry_on_startup=True,
        worker_prefetch_multiplier=1,
        accept_content=["json"],
        task_serializer="json",
        result_serializer="json",

        # Redis-backed Celery Beat scheduler
        redbeat_redis_url=os.getenv(
            "REDBEAT_REDIS_URL",
            "redis://localhost:6380/2",
        ),
        redbeat_key_prefix="meridian:redbeat",
        redbeat_lock_timeout=1500,
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
