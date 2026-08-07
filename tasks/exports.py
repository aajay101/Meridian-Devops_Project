"""
CSV export Celery task.

Orchestrates the export workflow: export -> return metadata.
"""
import logging

from celery_worker import celery
from services.export_service import cleanup_old_exports, export_student_history

logger = logging.getLogger(__name__)


@celery.task(name="tasks.exports.export_applications_csv", bind=True, max_retries=3)
def export_applications_csv(self, student_profile_id):
    """
    Export all placement applications for a student to CSV.

    Parameters:
        self (Celery task instance — bind=True)
        student_profile_id (int)

    Returns:
        dict {
            "success": bool — True if export completed
            "filename": str — exported CSV filename
            "filepath": str — absolute filepath to CSV
            "record_count": int — number of records exported
        }

    Raises:
        ValueError — if student not found (NOT retried)
        IOError — if export fails (retried up to 3 times)
        sqlalchemy.exc.OperationalError — if DB fails (retried up to 3 times)

    Retry:
        Retries on IOError and OperationalError with 60-second countdown.
        Does NOT retry on ValueError or programming errors.

    Side Effects:
        Creates CSV file in static/exports/
    """
    task_id = self.request.id
    logger.info("[%s] Export task started for student_profile_id=%s", task_id, student_profile_id)

    try:
        result = export_student_history(student_profile_id)
    except (IOError, OSError) as exc:
        logger.error("[%s] Export failed (filesystem) for student_profile_id=%s: %s", task_id, student_profile_id, exc)
        raise self.retry(exc=exc, countdown=60)
    except ValueError:
        raise
    except Exception as exc:
        logger.error("[%s] Export failed for student_profile_id=%s: %s", task_id, student_profile_id, exc)
        raise self.retry(exc=exc, countdown=60)

    cleanup_old_exports()

    logger.info("[%s] Export completed: filename=%s records=%d student=%s", task_id, result["filename"], result["record_count"], student_profile_id)

    return {
        "success": True,
        "filename": result["filename"],
        "filepath": result["filepath"],
        "record_count": result["record_count"],
    }
