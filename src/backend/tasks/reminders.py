import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from celery_worker import celery, flask_app
from models import Application, CompanyProfile, PlacementDrive, ReminderRun, StudentProfile, User, db
from sqlalchemy import and_, or_, update
from sqlalchemy.exc import IntegrityError
from utils.email_utils import build_reminder_email, send_bulk_emails
from utils.validators import check_eligibility

logger = logging.getLogger(__name__)

_STALE_RUN_AFTER = timedelta(hours=1)


def _local_today():
    try:
        zone = ZoneInfo(flask_app.config.get("CELERY_TIMEZONE", "UTC"))
    except (ZoneInfoNotFoundError, ValueError):
        zone = timezone.utc
    return datetime.now(zone).date()


def _local_deadline_string(value):
    try:
        zone = ZoneInfo(flask_app.config.get("CELERY_TIMEZONE", "UTC"))
    except (ZoneInfoNotFoundError, ValueError):
        zone = timezone.utc
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(zone).strftime("%B %d, %Y")


def _claim_daily_run(run_date):
    now = datetime.now(timezone.utc)
    existing = db.session.get(ReminderRun, run_date)
    if existing:
        if existing.status == "completed":
            return False
        stale_cutoff = now - _STALE_RUN_AFTER
        claimable = or_(
            ReminderRun.status == "failed",
            and_(
                ReminderRun.status == "running",
                ReminderRun.started_at <= stale_cutoff,
            ),
        )
        claimed = db.session.execute(
            update(ReminderRun)
            .where(
                ReminderRun.run_date == run_date,
                claimable,
            )
            .values(status="running", started_at=now, completed_at=None)
            .execution_options(synchronize_session=False)
        )
        if claimed.rowcount != 1:
            db.session.rollback()
            return False
    else:
        db.session.add(ReminderRun(run_date=run_date, status="running", started_at=now))

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return False
    return True


def _finish_daily_run(run_date, success):
    run = db.session.get(ReminderRun, run_date)
    if not run:
        return
    run.status = "completed" if success else "failed"
    run.completed_at = datetime.now(timezone.utc)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Failed to persist reminder run status for %s", run_date)


@celery.task(name="tasks.reminders.send_daily_reminders", bind=True, max_retries=3)
def send_daily_reminders(self):
    window_days = flask_app.config.get("REMINDER_WINDOW_DAYS", 3)
    now = datetime.now(timezone.utc)
    deadline_limit = now + timedelta(days=window_days)
    run_date = _local_today()

    if not _claim_daily_run(run_date):
        logger.info("Daily reminders already claimed or completed for %s", run_date)
        return {"drives_found": 0, "emails_queued": 0, "skipped": "already_run"}

    upcoming_drives = (
        PlacementDrive.query
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .join(User, CompanyProfile.user_id == User.id)
        .filter(
            PlacementDrive.status == "Approved",
            CompanyProfile.approval_status == "Approved",
            User.is_active.is_(True),
            PlacementDrive.application_deadline > now,
            PlacementDrive.application_deadline <= deadline_limit,
        )
        .all()
    )

    if not upcoming_drives:
        logger.info("No upcoming drives found — no reminders to send")
        _finish_daily_run(run_date, True)
        return {"drives_found": 0, "emails_queued": 0}

    students = (
        db.session.query(StudentProfile, User)
        .join(User, StudentProfile.user_id == User.id)
        .filter(User.is_active == True)
        .all()
    )

    if not students:
        logger.info("No active students found — no reminders to send")
        _finish_daily_run(run_date, True)
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
        deadline_str = _local_deadline_string(drive.application_deadline)

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
        _finish_daily_run(run_date, True)
        return {"drives_found": len(upcoming_drives), "emails_queued": 0}

    result = send_bulk_emails(messages)
    logger.info(
        "Daily reminders complete: %d emails queued, %d sent, %d failed",
        len(messages), result["sent"], result["failed"],
    )
    if result["failed"] and result["sent"] == 0:
        _finish_daily_run(run_date, False)
        raise self.retry(
            exc=RuntimeError("All daily reminder emails failed"),
            countdown=300,
        )

    _finish_daily_run(run_date, result["failed"] == 0)
    return {
        "drives_found": len(upcoming_drives),
        "emails_queued": len(messages),
        "sent": result["sent"],
        "failed": result["failed"],
    }
