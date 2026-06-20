from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_login import current_user

from models import Application, CompanyProfile, PlacementDrive, StudentProfile, User, db
from utils.validators import company_required

company_bp = Blueprint("company", __name__)


@company_bp.route("/health")
def health():
    return jsonify({"status": "ok", "scope": "company"})


@company_bp.route("/profile")
@company_required
def get_profile():
    cp = _get_company_profile()
    if not cp:
        return jsonify({"success": False, "error": "no_company_profile"}), 403

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
    required = ["job_title", "job_description", "eligibility_branch",
                 "eligibility_cgpa", "eligibility_year", "application_deadline"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"success": False, "error": "missing_fields", "fields": missing}), 400

    errors = []
    _check_string(data, "job_title", 120, errors)
    _check_string(data, "eligibility_branch", 80, errors)
    if errors:
        return jsonify({"success": False, "error": "string_too_long", "details": errors}), 400

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

    drive = PlacementDrive(
        company_profile_id=cp.id,
        job_title=data["job_title"],
        job_description=data["job_description"],
        eligibility_branch=data["eligibility_branch"],
        eligibility_cgpa=eligibility_cgpa,
        eligibility_year=eligibility_year,
        application_deadline=deadline,
        status="Pending",
    )
    db.session.add(drive)
    db.session.commit()

    return jsonify({"success": True, "drive_id": drive.id, "status": drive.status}), 201


@company_bp.route("/drives", methods=["GET"])
@company_required
def list_drives():
    cp = _get_company_profile()
    if not cp:
        return jsonify({"success": False, "error": "no_company_profile"}), 403

    drives = (
        PlacementDrive.query
        .filter_by(company_profile_id=cp.id)
        .order_by(PlacementDrive.created_at.desc())
        .all()
    )
    return jsonify({
        "success": True,
        "drives": [
            {
                "drive_id": d.id,
                "job_title": d.job_title,
                "job_description": d.job_description,
                "eligibility_branch": d.eligibility_branch,
                "eligibility_cgpa": d.eligibility_cgpa,
                "eligibility_year": d.eligibility_year,
                "application_deadline": d.application_deadline.isoformat(),
                "status": d.status,
                "created_at": d.created_at.isoformat(),
            }
            for d in drives
        ],
    })


@company_bp.route("/drives/<int:drive_id>", methods=["GET"])
@company_required
def get_drive(drive_id):
    try:
        cp, drive = _get_owned_drive(drive_id)
    except _DriveAccessError as e:
        return jsonify({"success": False, "error": e.error}), e.status_code

    return jsonify({
        "success": True,
        "drive": {
            "drive_id": drive.id,
            "job_title": drive.job_title,
            "job_description": drive.job_description,
            "eligibility_branch": drive.eligibility_branch,
            "eligibility_cgpa": drive.eligibility_cgpa,
            "eligibility_year": drive.eligibility_year,
            "application_deadline": drive.application_deadline.isoformat(),
            "status": drive.status,
            "created_at": drive.created_at.isoformat(),
        },
    })


@company_bp.route("/drives/<int:drive_id>", methods=["PUT"])
@company_required
def edit_drive(drive_id):
    try:
        cp, drive = _get_owned_drive(drive_id)
    except _DriveAccessError as e:
        return jsonify({"success": False, "error": e.error}), e.status_code

    if drive.status != "Pending":
        return jsonify({"success": False, "error": "drive_not_editable"}), 400

    data = request.get_json(silent=True) or {}

    errors = []
    _check_string(data, "job_title", 120, errors)
    _check_string(data, "eligibility_branch", 80, errors)
    if errors:
        return jsonify({"success": False, "error": "string_too_long", "details": errors}), 400

    if "job_title" in data:
        drive.job_title = data["job_title"]
    if "job_description" in data:
        drive.job_description = data["job_description"]
    if "eligibility_branch" in data:
        drive.eligibility_branch = data["eligibility_branch"]
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
    if "application_deadline" in data:
        try:
            drive.application_deadline = datetime.fromisoformat(data["application_deadline"])
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "invalid_deadline_format"}), 400

    db.session.commit()
    return jsonify({"success": True, "drive_id": drive.id})


@company_bp.route("/drives/<int:drive_id>", methods=["DELETE"])
@company_required
def delete_drive(drive_id):
    try:
        cp, drive = _get_owned_drive(drive_id)
    except _DriveAccessError as e:
        return jsonify({"success": False, "error": e.error}), e.status_code

    if drive.status not in ("Pending", "Rejected"):
        return jsonify({"success": False, "error": "drive_not_deletable"}), 400

    db.session.delete(drive)
    db.session.commit()
    return jsonify({"success": True})


@company_bp.route("/drives/<int:drive_id>/close", methods=["POST"])
@company_required
def close_drive(drive_id):
    try:
        cp, drive = _get_owned_drive(drive_id)
    except _DriveAccessError as e:
        return jsonify({"success": False, "error": e.error}), e.status_code

    if drive.status != "Approved":
        return jsonify({"success": False, "error": "drive_not_closable"}), 400

    drive.status = "Closed"
    db.session.commit()
    return jsonify({"success": True, "drive_id": drive.id, "status": drive.status})


@company_bp.route("/drives/<int:drive_id>/applicants", methods=["GET"])
@company_required
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
            "application_date": a.application_date.isoformat(),
        })
    return jsonify({"success": True, "applicants": result})


@company_bp.route("/drives/<int:drive_id>/applicants/count", methods=["GET"])
@company_required
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
        return jsonify({"success": False, "error": "already_finalized"}), 400

    app.status = "Shortlisted"
    db.session.commit()
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
        return jsonify({"success": False, "error": "already_finalized"}), 400

    data = request.get_json(silent=True) or {}
    app.status = "Rejected"
    app.selection_date = datetime.now(timezone.utc)
    if data.get("remarks"):
        app.remarks = data["remarks"]
    db.session.commit()
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
        return jsonify({"success": False, "error": "already_finalized"}), 400

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
    db.session.commit()
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
        return jsonify({"success": False, "error": "already_finalized"}), 400

    data = request.get_json(silent=True) or {}
    app.status = "Selected"
    app.selection_date = datetime.now(timezone.utc)
    if data.get("remarks"):
        app.remarks = data["remarks"]
    db.session.commit()
    return jsonify({"success": True, "application_id": app.id, "status": app.status})
