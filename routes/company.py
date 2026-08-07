from datetime import datetime, timezone

import json
from flask import Blueprint, jsonify, request
from flask_login import current_user
from sqlalchemy import func

from models import Application, CompanyProfile, PlacementDrive, db
from utils.cache_utils import (
    cache,
    invalidate_admin_companies,
    invalidate_admin_drives,
    invalidate_application_status,
    invalidate_company_applicants,
    invalidate_company_drive,
    invalidate_company_profile,
    invalidate_drive_created,
    invalidate_drive_deleted,
    invalidate_drive_status,
)
from utils.validators import company_required, validate_branches

company_bp = Blueprint("company", __name__)


def _safe_json_loads(raw, default=None):
    if not raw:
        return default if default is not None else []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


@company_bp.route("/health")
def health():
    return jsonify({"status": "ok", "scope": "company"})


@company_bp.route("/profile")
@company_required
def get_profile():
    cp = _get_company_profile()
    if not cp:
        return jsonify({"success": False, "error": "no_company_profile"}), 403

    cache_key = f"company:{cp.id}:profile"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached)

    u = cp.user
    response = {
        "success": True,
        "company": {
            "company_profile_id": cp.id,
            "company_name": cp.company_name,
            "hr_contact": cp.hr_contact,
            "website": cp.website,
            "approval_status": cp.approval_status,
            "email": u.email,
            "created_at": cp.created_at.isoformat(),
        },
    }
    cache.set(cache_key, response, timeout=300)
    return jsonify(response)


@company_bp.route("/profile", methods=["PUT"])
@company_required
def update_profile():
    cp = _get_company_profile()
    if not cp:
        return jsonify({"success": False, "error": "no_company_profile"}), 403

    data = request.get_json(silent=True) or {}
    errors = []

    if "company_name" in data:
        val = data["company_name"]
        if not val or not isinstance(val, str) or not val.strip():
            errors.append("company_name is required")
        elif len(val) > 120:
            errors.append("company_name must be 120 characters or less")

    if "hr_contact" in data:
        val = data["hr_contact"]
        if not val or not isinstance(val, str) or not val.strip():
            errors.append("hr_contact is required")
        elif len(val) > 120:
            errors.append("hr_contact must be 120 characters or less")

    if "website" in data:
        val = data["website"]
        if val is not None and val != "" and isinstance(val, str) and len(val) > 255:
            errors.append("website must be 255 characters or less")

    if errors:
        return jsonify({"success": False, "error": "validation_failed", "details": errors}), 400

    if "company_name" in data:
        cp.company_name = data["company_name"].strip()
    if "hr_contact" in data:
        cp.hr_contact = data["hr_contact"].strip()
    if "website" in data:
        cp.website = data["website"].strip() if data["website"] else None

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_company_profile(cp.id)
    invalidate_admin_companies()

    u = cp.user
    return jsonify({
        "success": True,
        "company": {
            "company_profile_id": cp.id,
            "company_name": cp.company_name,
            "hr_contact": cp.hr_contact,
            "website": cp.website,
            "approval_status": cp.approval_status,
            "email": u.email,
            "created_at": cp.created_at.isoformat(),
        },
    })


@company_bp.route("/protected")
@company_required
def protected():
    return jsonify({"success": True, "scope": "company"})


@company_bp.route("/dashboard")
@company_required
def dashboard():
    cp = current_user.company_profile
    if not cp:
        return jsonify({"success": False, "error": "no_company_profile"}), 403

    cache_key = f"company:{cp.id}:dashboard"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached)

    drives = PlacementDrive.query.filter_by(company_profile_id=cp.id).all()

    total_drives = len(drives)
    approved = sum(1 for d in drives if d.status == "Approved")
    pending = sum(1 for d in drives if d.status == "Pending")
    closed = sum(1 for d in drives if d.status == "Closed")

    drive_ids = [d.id for d in drives]
    applicant_counts = {}
    if drive_ids:
        rows = (
            db.session.query(Application.drive_id, func.count(Application.id))
            .filter(Application.drive_id.in_(drive_ids))
            .group_by(Application.drive_id)
            .all()
        )
        applicant_counts = dict(rows)

    total_applicants = sum(applicant_counts.values())

    recent = sorted(drives, key=lambda d: d.created_at, reverse=True)[:5]
    recent_drives = [
        {
            "drive_id": d.id,
            "job_title": d.job_title,
            "status": d.status,
            "application_deadline": d.application_deadline.isoformat(),
            "applicants": applicant_counts.get(d.id, 0),
        }
        for d in recent
    ]

    response = {
        "success": True,
        "total_drives": total_drives,
        "approved_drives": approved,
        "pending_drives": pending,
        "closed_drives": closed,
        "total_applicants": total_applicants,
        "recent_drives": recent_drives,
    }
    cache.set(cache_key, response, timeout=120)
    return jsonify(response)


def _get_company_profile():
    return current_user.company_profile


def _get_owned_drive(drive_id):
    """Returns (company_profile, drive) or raises _DriveAccessError."""
    cp = _get_company_profile()
    if not cp:
        raise _DriveAccessError("no_company_profile", 403)
    drive = db.session.get(PlacementDrive, drive_id)
    if not drive:
        raise _DriveAccessError("not_found", 404)
    if drive.company_profile_id != cp.id:
        raise _DriveAccessError("forbidden", 403)
    return cp, drive


class _DriveAccessError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def _parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_int(value):
    if isinstance(value, float) and not value.is_integer():
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _check_string(data, field, max_length, errors):
    val = data.get(field)
    if val is not None and isinstance(val, str) and len(val) > max_length:
        errors.append(f"{field} exceeds {max_length} characters")


@company_bp.route("/drives", methods=["POST"])
@company_required
def create_drive():
    cp = _get_company_profile()
    if not cp:
        return jsonify({"success": False, "error": "no_company_profile"}), 403

    if cp.approval_status != "Approved":
        return jsonify({"success": False, "error": "company_not_approved"}), 403

    data = request.get_json(silent=True) or {}
    required = ["job_title", "job_description", "eligibility_branches",
                 "eligibility_cgpa", "eligibility_year", "application_deadline"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"success": False, "error": "missing_fields", "fields": missing}), 400

    errors = []
    _check_string(data, "job_title", 120, errors)
    if errors:
        return jsonify({"success": False, "error": "string_too_long", "details": errors}), 400

    if not validate_branches(data["eligibility_branches"]):
        return jsonify({"success": False, "error": "invalid_branches"}), 400

    try:
        deadline = datetime.fromisoformat(data["application_deadline"])
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "invalid_deadline_format"}), 400

    eligibility_cgpa = _parse_float(data["eligibility_cgpa"])
    if eligibility_cgpa is None:
        return jsonify({"success": False, "error": "invalid_eligibility_cgpa"}), 400

    eligibility_year = _parse_int(data["eligibility_year"])
    if eligibility_year is None:
        return jsonify({"success": False, "error": "invalid_eligibility_year"}), 400

    eligibility_year_mode = data.get("eligibility_year_mode", "exact")
    if eligibility_year_mode not in ("exact", "minimum"):
        return jsonify({"success": False, "error": "invalid_eligibility_year_mode"}), 400

    eligibility_branches_json = json.dumps(data["eligibility_branches"])
    eligibility_branch = data["eligibility_branches"][0]

    drive = PlacementDrive(
        company_profile_id=cp.id,
        job_title=data["job_title"],
        job_description=data["job_description"],
        eligibility_branches=eligibility_branches_json,
        eligibility_branch=eligibility_branch,
        eligibility_cgpa=eligibility_cgpa,
        eligibility_year=eligibility_year,
        eligibility_year_mode=eligibility_year_mode,
        application_deadline=deadline,
        status="Pending",
    )
    db.session.add(drive)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_drive_created(cp.id)

    return jsonify({"success": True, "drive_id": drive.id, "status": drive.status}), 201


@company_bp.route("/drives", methods=["GET"])
@company_required
def list_drives():
    cp = _get_company_profile()
    if not cp:
        return jsonify({"success": False, "error": "no_company_profile"}), 403

    cache_key = f"company:{cp.id}:drives"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached)

    drives = (
        PlacementDrive.query
        .filter_by(company_profile_id=cp.id)
        .order_by(PlacementDrive.created_at.desc())
        .all()
    )
    response = {
        "success": True,
        "drives": [
            {
                "drive_id": d.id,
                "job_title": d.job_title,
                "job_description": d.job_description,
                "eligibility_branches": _safe_json_loads(d.eligibility_branches),
                "eligibility_branch": d.eligibility_branch,
                "eligibility_cgpa": d.eligibility_cgpa,
                "eligibility_year": d.eligibility_year,
                "eligibility_year_mode": d.eligibility_year_mode,
                "application_deadline": d.application_deadline.isoformat(),
                "status": d.status,
                "created_at": d.created_at.isoformat(),
            }
            for d in drives
        ],
    }
    cache.set(cache_key, response, timeout=120)
    return jsonify(response)


@company_bp.route("/drives/<int:drive_id>", methods=["GET"])
@company_required
def get_drive(drive_id):
    try:
        cp, drive = _get_owned_drive(drive_id)
    except _DriveAccessError as e:
        return jsonify({"success": False, "error": e.error}), e.status_code

    cache_key = f"company:{cp.id}:drive:{drive_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached)

    response = {
        "success": True,
        "drive": {
            "drive_id": drive.id,
            "job_title": drive.job_title,
            "job_description": drive.job_description,
            "eligibility_branches": _safe_json_loads(drive.eligibility_branches),
            "eligibility_branch": drive.eligibility_branch,
            "eligibility_cgpa": drive.eligibility_cgpa,
            "eligibility_year": drive.eligibility_year,
            "eligibility_year_mode": drive.eligibility_year_mode,
            "application_deadline": drive.application_deadline.isoformat(),
            "status": drive.status,
            "created_at": drive.created_at.isoformat(),
        },
    }
    cache.set(cache_key, response, timeout=300)
    return jsonify(response)


@company_bp.route("/drives/<int:drive_id>", methods=["PUT"])
@company_required
def edit_drive(drive_id):
    try:
        cp, drive = _get_owned_drive(drive_id)
    except _DriveAccessError as e:
        return jsonify({"success": False, "error": e.error}), e.status_code

    if drive.status != "Pending":
        return jsonify({"success": False, "error": "drive_not_editable"}), 409

    data = request.get_json(silent=True) or {}

    errors = []
    _check_string(data, "job_title", 120, errors)
    if errors:
        return jsonify({"success": False, "error": "string_too_long", "details": errors}), 400

    if "eligibility_branches" in data:
        if not validate_branches(data["eligibility_branches"]):
            return jsonify({"success": False, "error": "invalid_branches"}), 400

    if "job_title" in data:
        drive.job_title = data["job_title"]
    if "job_description" in data:
        drive.job_description = data["job_description"]
    if "eligibility_branches" in data:
        drive.eligibility_branches = json.dumps(data["eligibility_branches"])
        drive.eligibility_branch = data["eligibility_branches"][0]
    if "eligibility_cgpa" in data:
        parsed_cgpa = _parse_float(data["eligibility_cgpa"])
        if parsed_cgpa is None:
            return jsonify({"success": False, "error": "invalid_eligibility_cgpa"}), 400
        drive.eligibility_cgpa = parsed_cgpa
    if "eligibility_year" in data:
        parsed_year = _parse_int(data["eligibility_year"])
        if parsed_year is None:
            return jsonify({"success": False, "error": "invalid_eligibility_year"}), 400
        drive.eligibility_year = parsed_year
    if "eligibility_year_mode" in data:
        mode = data["eligibility_year_mode"]
        if mode not in ("exact", "minimum"):
            return jsonify({"success": False, "error": "invalid_eligibility_year_mode"}), 400
        drive.eligibility_year_mode = mode
    if "application_deadline" in data:
        try:
            drive.application_deadline = datetime.fromisoformat(data["application_deadline"])
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "invalid_deadline_format"}), 400

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_company_drive(cp.id, drive.id)
    invalidate_admin_drives()

    return jsonify({"success": True, "drive_id": drive.id})


@company_bp.route("/drives/<int:drive_id>", methods=["DELETE"])
@company_required
def delete_drive(drive_id):
    try:
        cp, drive = _get_owned_drive(drive_id)
    except _DriveAccessError as e:
        return jsonify({"success": False, "error": e.error}), e.status_code

    if drive.status not in ("Pending", "Rejected"):
        return jsonify({"success": False, "error": "drive_not_deletable"}), 409

    db.session.delete(drive)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_drive_deleted(cp.id, drive.id)

    return jsonify({"success": True})


@company_bp.route("/drives/<int:drive_id>/close", methods=["POST"])
@company_required
def close_drive(drive_id):
    try:
        cp, drive = _get_owned_drive(drive_id)
    except _DriveAccessError as e:
        return jsonify({"success": False, "error": e.error}), e.status_code

    if drive.status != "Approved":
        return jsonify({"success": False, "error": "drive_not_closable"}), 409

    drive.status = "Closed"
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_drive_status(cp.id, drive.id)

    return jsonify({"success": True, "drive_id": drive.id, "status": drive.status})


@company_bp.route("/drives/<int:drive_id>/applicants", methods=["GET"])
@company_required
@cache.cached(timeout=60, key_prefix=lambda: f"company:drive:{request.view_args.get('drive_id', 'unknown')}:applicants")
def list_applicants(drive_id):
    try:
        cp, drive = _get_owned_drive(drive_id)
    except _DriveAccessError as e:
        return jsonify({"success": False, "error": e.error}), e.status_code

    apps = (
        Application.query
        .filter_by(drive_id=drive.id)
        .order_by(Application.application_date.asc())
        .all()
    )
    result = []
    for a in apps:
        sp = a.student_profile
        u = sp.user
        result.append({
            "application_id": a.id,
            "student_profile_id": sp.id,
            "student_name": sp.name,
            "student_email": u.email,
            "branch": sp.branch,
            "cgpa": sp.cgpa,
            "year": sp.year,
            "status": a.status,
            "offer_status": a.offer_status,
            "application_date": a.application_date.isoformat(),
            "resume_path": a.resume_path,
            "interview_datetime": a.interview_datetime.isoformat() if a.interview_datetime else None,
            "interview_location": a.interview_location,
        })
    return jsonify({"success": True, "applicants": result})


@company_bp.route("/drives/<int:drive_id>/applicants/count", methods=["GET"])
@company_required
@cache.cached(timeout=60, key_prefix=lambda: f"company:drive:{request.view_args.get('drive_id', 'unknown')}:count")
def applicant_count(drive_id):
    try:
        cp, drive = _get_owned_drive(drive_id)
    except _DriveAccessError as e:
        return jsonify({"success": False, "error": e.error}), e.status_code

    count = Application.query.filter_by(drive_id=drive.id).count()
    return jsonify({"success": True, "drive_id": drive.id, "count": count})


@company_bp.route("/application/<int:application_id>/shortlist", methods=["POST"])
@company_required
def shortlist_application(application_id):
    app = db.session.get(Application, application_id)
    if not app:
        return jsonify({"success": False, "error": "not_found"}), 404

    drive = app.drive
    cp = _get_company_profile()
    if not cp or drive.company_profile_id != cp.id:
        return jsonify({"success": False, "error": "forbidden"}), 403

    if app.status != "Applied":
        return jsonify({"success": False, "error": "already_finalized"}), 409

    app.status = "Shortlisted"
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_application_status(app.student_profile.user_id, drive.id)
    invalidate_company_applicants(drive.id)

    return jsonify({"success": True, "application_id": app.id, "status": app.status})


@company_bp.route("/application/<int:application_id>/reject", methods=["POST"])
@company_required
def reject_application(application_id):
    app = db.session.get(Application, application_id)
    if not app:
        return jsonify({"success": False, "error": "not_found"}), 404

    drive = app.drive
    cp = _get_company_profile()
    if not cp or drive.company_profile_id != cp.id:
        return jsonify({"success": False, "error": "forbidden"}), 403

    if app.status not in ("Applied", "Shortlisted", "Interview Scheduled"):
        return jsonify({"success": False, "error": "already_finalized"}), 409

    data = request.get_json(silent=True) or {}
    app.status = "Rejected"
    app.selection_date = datetime.now(timezone.utc)
    if data.get("remarks"):
        app.remarks = data["remarks"]
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_application_status(app.student_profile.user_id, drive.id)
    invalidate_company_applicants(drive.id)

    return jsonify({"success": True, "application_id": app.id, "status": app.status})


@company_bp.route("/application/<int:application_id>/schedule-interview", methods=["POST"])
@company_required
def schedule_interview(application_id):
    app = db.session.get(Application, application_id)
    if not app:
        return jsonify({"success": False, "error": "not_found"}), 404

    drive = app.drive
    cp = _get_company_profile()
    if not cp or drive.company_profile_id != cp.id:
        return jsonify({"success": False, "error": "forbidden"}), 403

    if app.status != "Shortlisted":
        return jsonify({"success": False, "error": "already_finalized"}), 409

    data = request.get_json(silent=True) or {}
    required = ["interview_datetime"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"success": False, "error": "missing_fields", "fields": missing}), 400

    try:
        dt = datetime.fromisoformat(data["interview_datetime"])
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "invalid_datetime_format"}), 400

    app.interview_datetime = dt
    app.interview_location = data.get("interview_location")
    app.status = "Interview Scheduled"
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_application_status(app.student_profile.user_id, drive.id)
    invalidate_company_applicants(drive.id)

    return jsonify({"success": True, "application_id": app.id, "status": app.status})


@company_bp.route("/application/<int:application_id>/select", methods=["POST"])
@company_required
def select_application(application_id):
    app = db.session.get(Application, application_id)
    if not app:
        return jsonify({"success": False, "error": "not_found"}), 404

    drive = app.drive
    cp = _get_company_profile()
    if not cp or drive.company_profile_id != cp.id:
        return jsonify({"success": False, "error": "forbidden"}), 403

    if app.status != "Interview Scheduled":
        return jsonify({"success": False, "error": "already_finalized"}), 409

    from flask import current_app
    max_offers = current_app.config.get("MAX_ACTIVE_OFFERS", 3)

    pending_offers = Application.query.filter_by(
        student_profile_id=app.student_profile_id,
        status="Selected",
        offer_status="Pending",
    ).count()
    if pending_offers >= max_offers:
        return jsonify({"success": False, "error": "max_offers_reached"}), 400

    data = request.get_json(silent=True) or {}
    app.status = "Selected"
    app.offer_status = "Pending"
    app.selection_date = datetime.now(timezone.utc)
    if data.get("remarks"):
        app.remarks = data["remarks"]
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_application_status(app.student_profile.user_id, drive.id, include_history=True)
    invalidate_company_applicants(drive.id)

    return jsonify({"success": True, "application_id": app.id, "status": app.status, "offer_status": app.offer_status})
