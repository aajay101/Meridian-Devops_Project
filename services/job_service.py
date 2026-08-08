"""
Export job status service.

Provides public functions to retrieve the status of an export job
and to resolve verified download paths.
Translates Celery task states into project-level responses.
"""
import logging
import os

from flask import current_app

logger = logging.getLogger(__name__)

# In-memory task registry: maps task_id -> student_profile_id.
# Populated by the route when a task is queued.
# Used by the service to verify ownership on every status check.
_task_registry = {}


def _verify_task_ownership(task_id, student_profile_id):
    """
    Verify task ownership and resolve Celery state.

    Centralizes the ownership check and Celery AsyncResult lookup
    used by both get_export_job_status() and resolve_download_path().

    Parameters:
        task_id (str)
        student_profile_id (int)

    Returns:
        dict {
            "authorized": bool,
            "status": str,  — TASK_NOT_FOUND | UNAUTHORIZED | Celery state
            "result": AsyncResult or None,
            "error": str or None,
        }
    """
    owner_id = _task_registry.get(task_id)
    if owner_id is None:
        logger.warning("Task not found in registry: task_id=%s", task_id)
        return {"authorized": False, "status": "TASK_NOT_FOUND", "result": None, "error": "Task not found"}

    if owner_id != student_profile_id:
        logger.warning(
            "Unauthorized access attempt: task_id=%s requested_by=%s owner=%s",
            task_id, student_profile_id, owner_id,
        )
        return {"authorized": False, "status": "UNAUTHORIZED", "result": None, "error": "Unauthorized access to this task"}

    from celery_worker import celery
    result = celery.AsyncResult(task_id)
    return {"authorized": True, "status": result.state, "result": result, "error": None}


def register_task(task_id, student_profile_id):
    """
    Register a task with its owning student.

    Parameters:
        task_id (str)
        student_profile_id (int)

    Side Effects:
        Stores mapping in _task_registry.
    """
    _task_registry[task_id] = student_profile_id
    logger.info("Task registered: task_id=%s student_profile_id=%s", task_id, student_profile_id)


def get_export_job_status(task_id, student_profile_id):
    """
    Retrieve the status of an export job.

    Verifies ownership before returning any data.
    Translates Celery states into project-level responses.

    Parameters:
        task_id (str)
        student_profile_id (int)

    Returns:
        dict {
            "task_id": str,
            "status": str,  — PENDING | STARTED | SUCCESS | FAILURE | RETRY | REVOKED | TASK_NOT_FOUND | UNAUTHORIZED
            "filename": str,  — only on SUCCESS
            "record_count": int,  — only on SUCCESS
            "download_url": str,  — only on SUCCESS
            "error": str,  — only on FAILURE | TASK_NOT_FOUND | UNAUTHORIZED
        }

    Raises:
        None — all errors returned in response dict.
    """
    auth = _verify_task_ownership(task_id, student_profile_id)
    if not auth["authorized"]:
        return {"task_id": task_id, "status": auth["status"], "error": auth["error"]}

    state = auth["status"]
    result = auth["result"]

    if state == "SUCCESS":
        return _build_success_response(task_id, result)
    elif state == "FAILURE":
        return _build_failure_response(task_id, result)
    else:
        return {"task_id": task_id, "status": state}


def _build_success_response(task_id, result):
    """
    Build response for completed task.

    Parameters:
        task_id (str)
        result (Celery AsyncResult)

    Returns:
        dict with task_id, status, filename, record_count, download_url
    """
    data = result.result
    if not isinstance(data, dict):
        logger.warning("Task result is not a dict: task_id=%s type=%s", task_id, type(data))
        return {"task_id": task_id, "status": "FAILURE", "error": "Invalid task result format"}
    return {
        "task_id": task_id,
        "status": "SUCCESS",
        "filename": data.get("filename"),
        "record_count": data.get("record_count"),
        "download_url": f"/api/jobs/export/download/{task_id}",
    }


def _build_failure_response(task_id, result):
    """
    Build response for failed task.

    Parameters:
        task_id (str)
        result (Celery AsyncResult)

    Returns:
        dict with task_id, status, error
    """
    error = str(result.result) if result.result else "Unknown error"
    return {"task_id": task_id, "status": "FAILURE", "error": error}


def resolve_download_path(task_id, student_profile_id):
    """
    Resolve and verify a download path for a completed export task.

    Performs ownership validation, status verification, filename sanitization,
    and file existence check. Returns the absolute filepath if all checks pass.

    Parameters:
        task_id (str)
        student_profile_id (int)

    Returns:
        dict {
            "status": str,  — SUCCESS | TASK_NOT_FOUND | UNAUTHORIZED | PENDING | FAILURE | FILE_MISSING
            "filepath": str,  — absolute path only on SUCCESS
            "filename": str,  — safe filename only on SUCCESS
            "error": str,  — on failure states
        }
    """
    auth = _verify_task_ownership(task_id, student_profile_id)
    if not auth["authorized"]:
        return {"status": auth["status"], "error": auth["error"]}

    state = auth["status"]
    result = auth["result"]

    if state == "FAILURE":
        error = str(result.result) if result.result else "Unknown error"
        return {"status": "FAILURE", "error": error}

    if state != "SUCCESS":
        return {"status": state, "error": f"Export is not ready (status: {state})"}

    data = result.result
    filename = data.get("filename") if isinstance(data, dict) else None
    if not filename:
        logger.warning("Download task has no filename: task_id=%s", task_id)
        return {"status": "FILE_MISSING", "error": "Export file information not found"}

    safe_filename = os.path.basename(filename)
    if safe_filename != filename:
        logger.warning(
            "Path traversal rejected: task_id=%s filename=%s",
            task_id, filename,
        )
        return {"status": "FILE_MISSING", "error": "Invalid export filename"}

    export_dir = os.path.join(current_app.root_path, "static", "exports")
    filepath = os.path.join(export_dir, safe_filename)

    if not os.path.isfile(filepath):
        logger.warning(
            "Export file missing on disk: task_id=%s filepath=%s",
            task_id, filepath,
        )
        return {"status": "FILE_MISSING", "error": "Export file not found on server"}

    return {"status": "SUCCESS", "filepath": filepath, "filename": safe_filename}
