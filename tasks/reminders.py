import logging
from datetime import datetime, timedelta, timezone

from celery_worker import celery, flask_app
from models import Application, PlacementDrive, StudentProfile, User, db
from utils.email_utils import build_reminder_email, send_bulk_emails
from utils.validators import check_eligibility

logger = logging.getLogger(__name__)


@celery.task(name="tasks.reminders.send_daily_reminders")
def send_daily_reminders():
    window_days = flask_app.config.get("REMINDER_WINDOW_DAYS", 3)
    now = datetime.now(timezone.utc)
    deadline_limit = now + timedelta(days=window_days)

    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.status == "Approved",
        PlacementDrive.application_deadline > now,
        PlacementDrive.application_deadline <= deadline_limit,
    ).all()

    if not upcoming_drives:
        logger.info("No upcoming drives found — no reminders to send")
        return {"drives_found": 0, "emails_queued": 0}

    students = (
        db.session.query(StudentProfile, User)
        .join(User, StudentProfile.user_id == User.id)
        .filter(User.is_active == True)
        .all()
    )

    if not students:
        logger.info("No active students found — no reminders to send")
        return {"drives_found": len(upcoming_drives), "emails_queued": 0}

    drive_ids = [d.id for d in upcoming_drives]
    student_ids = [sp.id for sp, _ in students]

    existing_apps = set(
        db.session.query(Application.student_profile_id, Application.drive_id)
        .filter(
            Application.drive_id.in_(drive_ids),
            Application.student_profile_id.in_(student_ids),
        )
        .all()
    )

    messages = []

    for drive in upcoming_drives:
        company = drive.company_profile
        deadline_str = drive.application_deadline.strftime("%B %d, %Y")

        for sp, user in students:
            violations = check_eligibility(sp, drive)
            if violations:
                continue

            if (sp.id, drive.id) in existing_apps:
                continue

            subject, html_body = build_reminder_email(
                sp.name, company.company_name, drive.job_title, deadline_str
            )
            messages.append((user.email, subject, html_body))

    if not messages:
        logger.info("No eligible students to remind — no emails to send")
        return {"drives_found": len(upcoming_drives), "emails_queued": 0}

    result = send_bulk_emails(messages)
    logger.info(
        "Daily reminders complete: %d emails queued, %d sent, %d failed",
        len(messages), result["sent"], result["failed"],
    )
    return {
        "drives_found": len(upcoming_drives),
        "emails_queued": len(messages),
        "sent": result["sent"],
        "failed": result["failed"],
    }
