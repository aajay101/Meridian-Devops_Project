import logging
import uuid

from flask import Blueprint, jsonify, send_file
from flask_login import current_user

from services.job_service import (
    get_export_job_status,
    register_task,
    resolve_download_path,
    unregister_task,
)
from utils.validators import student_required

logger = logging.getLogger(__name__)

jobs_bp = Blueprint("jobs", __name__)


def _job_status_code(status, *, download=False):
    if status == "UNAUTHORIZED":
        return 403
    if status == "TASK_NOT_FOUND":
        return 404
    if status in {"FAILURE", "REVOKED"}:
        return 502
    if download and status != "SUCCESS":
        return 409
    return 200


@jobs_bp.route("/health")
def health():
    return jsonify({"status": "ok", "scope": "jobs"})


@jobs_bp.route("/export", methods=["POST"])
@student_required
def trigger_export():
    """
    Trigger async CSV export for the authenticated student.

    Returns 202 with task_id for polling.
    Student profile ID is derived from the authenticated session —
    no client-supplied ID is accepted.

    Raises:
        401 — unauthenticated (handled by @student_required)
        403 — no student profile linked to account
        502 — Celery broker unavailable (OperationalError)
    """
    from celery.exceptions import OperationalError
    from tasks.exports import export_applications_csv

    sp = current_user.student_profile
    if sp is None:
        logger.warning("Export requested by user %s with no student profile", current_user.id)
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    logger.info("Export requested by student_profile_id=%s", sp.id)

    task_id = str(uuid.uuid4())
    try:
        register_task(task_id, sp.id)
    except Exception:
        logger.error("Export ownership registration failed for student_profile_id=%s", sp.id)
        return jsonify({"success": False, "error": "export_registry_failed"}), 503

    try:
        result = export_applications_csv.apply_async(args=[sp.id], task_id=task_id)
    except OperationalError:
        unregister_task(task_id)
        logger.error("Celery broker unavailable — export failed for student_profile_id=%s", sp.id)
        return jsonify({"success": False, "error": "celery_queue_failed"}), 502
    except Exception:
        unregister_task(task_id)
        logger.exception("Export queue submission failed for student_profile_id=%s", sp.id)
        return jsonify({"success": False, "error": "celery_queue_failed"}), 502

    queued_task_id = getattr(result, "id", None)
    if queued_task_id != task_id:
        unregister_task(task_id)
        try:
            result.revoke()
        except Exception:
            logger.warning("Could not revoke mismatched export task: task_id=%s", queued_task_id)
        logger.error(
            "Celery returned a mismatched export task ID: requested=%s returned=%s",
            task_id,
            queued_task_id,
        )
        return jsonify({"success": False, "error": "celery_task_id_mismatch"}), 502

    logger.info("Export task queued: task_id=%s student_profile_id=%s", task_id, sp.id)

    return jsonify({
        "success": True,
        "message": "Export job queued successfully",
        "task_id": task_id,
        "job_type": "csv_export",
        "status": "PENDING",
    }), 202


@jobs_bp.route("/export/status/<task_id>")
@student_required
def get_export_status(task_id):
    """
    Retrieve the status of an export job.

    Returns 200 with task status from the service.
    Ownership validation is performed inside the service.

    Raises:
        401 — unauthenticated (handled by @student_required)
        403 — no student profile linked to account
    """
    sp = current_user.student_profile
    if sp is None:
        logger.warning("Export status requested by user %s with no student profile", current_user.id)
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    logger.info("Export status requested: task_id=%s student_profile_id=%s", task_id, sp.id)

    result = get_export_job_status(task_id, sp.id)

    return jsonify(result), _job_status_code(result.get("status"))


@jobs_bp.route("/export/download/<task_id>")
@student_required
def download_export(task_id):
    """
    Download the CSV file for a completed export task.

    Returns the CSV file as an attachment download.
    Ownership, status, and file safety are verified by the service.

    Raises:
        401 — unauthenticated (handled by @student_required)
        403 — no student profile linked to account
    """
    sp = current_user.student_profile
    if sp is None:
        logger.warning("Export download requested by user %s with no student profile", current_user.id)
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    logger.info("Export download requested: task_id=%s student_profile_id=%s", task_id, sp.id)

    result = resolve_download_path(task_id, sp.id)

    if result["status"] != "SUCCESS":
        return jsonify(result), _job_status_code(result.get("status"), download=True)

    try:
        return send_file(
            result["filepath"],
            mimetype="text/csv",
            as_attachment=True,
            download_name=result["filename"],
        )
    except FileNotFoundError:
        return jsonify({"success": False, "error": "file_missing"}), 404
