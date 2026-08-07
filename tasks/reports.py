import logging

from celery_worker import celery, flask_app
from services.report_service import (
    _get_previous_month,
    build_monthly_report_html,
    collect_monthly_stats,
)
from utils.email_utils import send_email

logger = logging.getLogger(__name__)


@celery.task(name="tasks.reports.send_monthly_report")
def send_monthly_report(year=None, month=None):
    if year is None or month is None:
        year, month = _get_previous_month()

    stats = collect_monthly_stats(year, month)
    html_body = build_monthly_report_html(stats)

    admin_email = flask_app.config.get("ADMIN_EMAIL", "admin@placement.local")
    subject = f"Monthly Placement Report — {stats['month_name']}"

    success = send_email(to=admin_email, subject=subject, html_body=html_body)

    if success:
        logger.info("Monthly report sent to %s for %s", admin_email, stats["month_name"])
    else:
        logger.error("Failed to send monthly report to %s for %s", admin_email, stats["month_name"])

    return {
        "success": success,
        "month_name": stats["month_name"],
        "recipient": admin_email,
        "drives_conducted": stats["drives_conducted"],
        "students_applied": stats["students_applied"],
        "students_selected": stats["students_selected"],
    }
