import logging

from flask import Blueprint, jsonify, send_file
from flask_login import current_user

from services.job_service import get_export_job_status, register_task, resolve_download_path
from utils.validators import student_required

logger = logging.getLogger(__name__)

jobs_bp = Blueprint("jobs", __name__)


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

    try:
        result = export_applications_csv.delay(sp.id)
    except OperationalError:
        logger.error("Celery broker unavailable — export failed for student_profile_id=%s", sp.id)
        return jsonify({"success": False, "error": "celery_queue_failed"}), 502

    logger.info("Export task queued: task_id=%s student_profile_id=%s", result.id, sp.id)

    register_task(result.id, sp.id)

    return jsonify({
        "success": True,
        "message": "Export job queued successfully",
        "task_id": result.id,
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

    return jsonify(result)


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
        return jsonify(result)

    try:
        return send_file(
            result["filepath"],
            mimetype="text/csv",
            as_attachment=True,
            download_name=result["filename"],
        )
    except FileNotFoundError:
        return jsonify({"success": False, "error": "file_missing"}), 404
