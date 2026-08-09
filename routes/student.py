import json
import math
import os
import uuid
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_login import current_user
from sqlalchemy import and_, asc, func, or_
from sqlalchemy.exc import IntegrityError

from models import Application, CompanyProfile, PlacementDrive, User, db
from utils.cache_utils import (
    cache,
    invalidate_application_created,
    invalidate_offer_status,
    invalidate_student_profile_data,
    invalidate_student_resume,
)
from utils.validators import (
    check_eligibility,
    escape_like,
    format_datetime,
    normalize_indian_phone_number,
    student_required,
    validate_branch,
)

student_bp = Blueprint("student", __name__)

MAX_RESUME_BYTES = 5 * 1024 * 1024


def _json_object():
    """Return a JSON object, an empty object for an empty body, or None."""
    data = request.get_json(silent=True)
    if data is None:
        return {} if not request.data else None
    return data if isinstance(data, dict) else None


def _check_string(data, field, max_length, errors):
    val = data.get(field)
    if val is not None and isinstance(val, str) and len(val) > max_length:
        errors.append(f"{field} exceeds {max_length} characters")


def _safe_json_loads(raw, default=None):
    if not raw:
        return default if default is not None else []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


def _as_utc(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _deadline_is_open(value, now=None):
    if value is None:
        return False
    now = now or datetime.now(timezone.utc)
    try:
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return _as_utc(value) >= now
    except (TypeError, ValueError):
        return False


@student_bp.route("/health")
def health():
    return jsonify({"status": "ok", "scope": "student"})


@student_bp.route("/protected")
@student_required
def protected():
    return jsonify({"success": True, "scope": "student"})


@student_bp.route("/dashboard")
@student_required
@cache.cached(timeout=60, key_prefix=lambda: f"student:{current_user.id}:dashboard")
def dashboard():
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    total_applications = Application.query.filter_by(student_profile_id=sp.id).count()

    status_counts = dict(
        db.session.query(Application.status, func.count(Application.id))
        .filter(Application.student_profile_id == sp.id)
        .group_by(Application.status)
        .all()
    )

    from flask import current_app
    max_offers = current_app.config.get("MAX_ACTIVE_OFFERS", 3)

    pending_offers = Application.query.filter_by(
        student_profile_id=sp.id,
        status="Selected",
        offer_status="Pending",
    ).count()

    return jsonify({
        "success": True,
        "profile": {
            "name": sp.name,
            "email": sp.user.email,
            "branch": sp.branch,
            "cgpa": sp.cgpa,
            "year": sp.year,
        },
        "total_applications": total_applications,
        "applied": status_counts.get("Applied", 0),
        "shortlisted": status_counts.get("Shortlisted", 0),
        "interview_scheduled": status_counts.get("Interview Scheduled", 0),
        "selected": status_counts.get("Selected", 0),
        "rejected": status_counts.get("Rejected", 0),
        "pending_offers": pending_offers,
        "max_active_offers": max_offers,
    })


def _get_student_profile():
    return current_user.student_profile


@student_bp.route("/profile", methods=["GET"])
@student_required
@cache.cached(timeout=300, key_prefix=lambda: f"student:{current_user.id}:profile")
def get_profile():
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    return jsonify({
        "success": True,
        "user_id": sp.user_id,
        "name": sp.name,
        "email": sp.user.email,
        "phone_number": sp.user.phone_number,
        "branch": sp.branch,
        "cgpa": sp.cgpa,
        "year": sp.year,
        "resume_path": sp.resume_path,
        "created_at": format_datetime(sp.created_at),
    })


@student_bp.route("/profile", methods=["PUT"])
@student_required
def update_profile():
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    data = _json_object()
    if data is None:
        return jsonify({"success": False, "error": "invalid_json_body"}), 400
    errors = []

    if "cgpa" in data:
        try:
            if isinstance(data["cgpa"], bool):
                raise ValueError
            cgpa = float(data["cgpa"])
            if not math.isfinite(cgpa) or cgpa < 0.0 or cgpa > 10.0:
                errors.append("cgpa must be between 0.0 and 10.0")
        except (TypeError, ValueError):
            errors.append("cgpa must be numeric")

    if "year" in data:
        raw = data["year"]
        if isinstance(raw, bool):
            errors.append("year must be an integer")
        elif isinstance(raw, float) and not raw.is_integer():
            errors.append("year must be an integer")
        else:
            try:
                year = int(raw)
                if year < 1 or year > 4:
                    errors.append("year must be between 1 and 4")
            except (TypeError, ValueError):
                errors.append("year must be an integer")

    if "name" in data:
        val = data["name"]
        if not isinstance(val, str):
            errors.append("name must be a string")
        elif not val.strip():
            errors.append("name is required")
        else:
            _check_string(data, "name", 120, errors)

    phone_number = None
    if "phone_number" in data:
        phone_number = normalize_indian_phone_number(data["phone_number"])
        if not phone_number:
            errors.append("phone_number must be a valid Indian mobile number")

    if errors:
        return jsonify({"success": False, "error": "validation_failed", "details": errors}), 400

    if "cgpa" in data:
        sp.cgpa = float(data["cgpa"])
    if "year" in data:
        sp.year = int(data["year"])
    if "name" in data:
        sp.name = data["name"].strip()
    if phone_number:
        existing_user = User.query.filter(
            User.phone_number == phone_number,
            User.id != current_user.id,
        ).first()
        if existing_user:
            return jsonify({"success": False, "error": "phone_number_exists"}), 409
        current_user.phone_number = phone_number
    if "branch" in data:
        if not validate_branch(data["branch"]):
            return jsonify({"success": False, "error": "invalid_branch"}), 400
        sp.branch = data["branch"]

    application_drive_ids = [application.drive_id for application in sp.applications]
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "phone_number_exists"}), 409
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_student_profile_data(current_user.id, application_drive_ids)

    return jsonify({
        "success": True,
        "user_id": sp.user_id,
        "name": sp.name,
        "email": sp.user.email,
        "phone_number": sp.user.phone_number,
        "branch": sp.branch,
        "cgpa": sp.cgpa,
        "year": sp.year,
        "created_at": format_datetime(sp.created_at),
    })


@student_bp.route("/profile/resume", methods=["POST"])
@student_required
def upload_resume():
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    if "file" not in request.files:
        return jsonify({"success": False, "error": "missing_file"}), 400

    file = request.files["file"]
    if file.filename == "" or file.filename is None:
        return jsonify({"success": False, "error": "missing_file"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "error": "invalid_file_type"}), 400

    # An extension alone is not enough: browsers cannot render arbitrary bytes as a PDF.
    if file.stream.read(5) != b"%PDF-":
        file.stream.seek(0)
        return jsonify({"success": False, "error": "invalid_file_type"}), 400
    file.stream.seek(0)

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_RESUME_BYTES:
        return jsonify({"success": False, "error": "file_too_large", "max_bytes": MAX_RESUME_BYTES}), 400

    unique_name = f"{uuid.uuid4().hex}.pdf"
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads", "resumes")
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, unique_name)
    try:
        file.save(save_path)
    except OSError:
        return jsonify({"success": False, "error": "save_failed"}), 500

    previous_resume_path = sp.resume_path

    sp.resume_path = "uploads/resumes/" + unique_name
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        try:
            os.remove(save_path)
        except OSError:
            pass
        return jsonify({"success": False, "error": "commit_failed"}), 500

    if previous_resume_path:
        old_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", previous_resume_path
        )
        try:
            resume_is_referenced = Application.query.filter_by(
                resume_path=previous_resume_path
            ).first() is not None
            if os.path.isfile(old_path) and not resume_is_referenced:
                os.remove(old_path)
        except OSError:
            pass

    invalidate_student_resume(current_user.id)

    return jsonify({
        "success": True,
        "stored_filename": unique_name,
        "stored_path": sp.resume_path,
    }), 201


@student_bp.route("/drives", methods=["GET"])
@student_required
def list_drives():
    q = request.args.get("q", "").strip()

    if not q:
        cached = cache.get("shared:drives_approved")
        if cached is not None:
            now = datetime.now(timezone.utc)
            return jsonify({
                **cached,
                "drives": [
                    drive for drive in cached.get("drives", [])
                    if _deadline_is_open(drive.get("application_deadline"), now)
                ],
            })

    now = datetime.now(timezone.utc)

    query = (
        db.session.query(PlacementDrive, CompanyProfile)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .join(User, CompanyProfile.user_id == User.id)
        .filter(PlacementDrive.status == "Approved")
        .filter(CompanyProfile.approval_status == "Approved", User.is_active.is_(True))
        .filter(PlacementDrive.application_deadline >= now)
    )
    if q:
        pattern = f"%{escape_like(q)}%"
        query = query.filter(
            or_(
                PlacementDrive.job_title.ilike(pattern, escape="\\"),
                PlacementDrive.job_description.ilike(pattern, escape="\\"),
                PlacementDrive.eligibility_branches.ilike(pattern, escape="\\"),
                PlacementDrive.eligibility_cgpa.cast(db.String).ilike(pattern, escape="\\"),
                CompanyProfile.company_name.ilike(pattern, escape="\\"),
            )
        )

    rows = query.order_by(asc(PlacementDrive.created_at)).all()
    result = []
    for d, cp in rows:
        result.append({
            "drive_id": d.id,
            "company_name": cp.company_name,
            "job_title": d.job_title,
            "job_description": d.job_description,
            "eligibility_branches": _safe_json_loads(d.eligibility_branches),
            "eligibility_branch": d.eligibility_branch,
            "eligibility_cgpa": d.eligibility_cgpa,
            "eligibility_year": d.eligibility_year,
            "eligibility_year_mode": d.eligibility_year_mode,
            "application_deadline": format_datetime(d.application_deadline),
            "created_at": format_datetime(d.created_at),
        })

    response = {"success": True, "drives": result}
    if not q:
        try:
            cache.set("shared:drives_approved", response, timeout=120)
        except Exception:
            pass

    return jsonify(response)


@student_bp.route("/drives/<int:drive_id>", methods=["GET"])
@student_required
@cache.cached(timeout=300, key_prefix=lambda: f"shared:drive:{request.view_args.get('drive_id', 'unknown')}")
def get_drive(drive_id):
    d = db.session.get(PlacementDrive, drive_id)
    if (
        not d
        or d.status != "Approved"
        or d.company_profile.approval_status != "Approved"
        or not d.company_profile.user.is_active
    ):
        return jsonify({"success": False, "error": "not_found"}), 404

    cp = d.company_profile
    return jsonify({
        "success": True,
        "drive": {
            "drive_id": d.id,
            "company_name": cp.company_name,
            "job_title": d.job_title,
            "job_description": d.job_description,
            "eligibility_branches": _safe_json_loads(d.eligibility_branches),
            "eligibility_branch": d.eligibility_branch,
            "eligibility_cgpa": d.eligibility_cgpa,
            "eligibility_year": d.eligibility_year,
            "eligibility_year_mode": d.eligibility_year_mode,
            "application_deadline": format_datetime(d.application_deadline),
            "created_at": format_datetime(d.created_at),
        },
    })


@student_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@student_required
def apply_to_drive(drive_id):
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    d = db.session.get(PlacementDrive, drive_id)
    if (
        not d
        or d.status != "Approved"
        or d.company_profile.approval_status != "Approved"
        or not d.company_profile.user.is_active
    ):
        return jsonify({"success": False, "error": "drive_not_available"}), 403

    if d.application_deadline:
        now = datetime.now(timezone.utc)
        deadline = d.application_deadline.replace(tzinfo=timezone.utc) if d.application_deadline.tzinfo is None else d.application_deadline
        if now > deadline:
            return jsonify({"success": False, "error": "deadline_passed"}), 400

    violations = check_eligibility(sp, d)
    if violations:
        return jsonify({"success": False, "error": "ineligible", "violations": violations}), 403

    existing = Application.query.filter_by(
        student_profile_id=sp.id, drive_id=d.id
    ).first()
    if existing:
        return jsonify({"success": False, "error": "already_applied"}), 409

    from flask import current_app
    max_offers = current_app.config.get("MAX_ACTIVE_OFFERS", 3)

    pending_offers = Application.query.filter_by(
        student_profile_id=sp.id,
        status="Selected",
        offer_status="Pending",
    ).count()
    if pending_offers >= max_offers:
        return jsonify({"success": False, "error": "max_offers_reached"}), 400

    resume_path = None
    save_path = None
    content_type = request.content_type or ""

    if "multipart/form-data" in content_type:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "missing_file"}), 400

        file = request.files["file"]
        if file.filename == "" or file.filename is None:
            return jsonify({"success": False, "error": "missing_file"}), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"success": False, "error": "invalid_file_type"}), 400

        if file.stream.read(5) != b"%PDF-":
            file.stream.seek(0)
            return jsonify({"success": False, "error": "invalid_file_type"}), 400
        file.stream.seek(0)

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > MAX_RESUME_BYTES:
            return jsonify({"success": False, "error": "file_too_large", "max_bytes": MAX_RESUME_BYTES}), 400

        unique_name = f"{uuid.uuid4().hex}.pdf"
        upload_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "uploads", "resumes"
        )
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, unique_name)
        try:
            file.save(save_path)
        except OSError:
            return jsonify({"success": False, "error": "save_failed"}), 500
        resume_path = "uploads/resumes/" + unique_name
    else:
        resume_path = sp.resume_path

    app = Application(
        student_profile_id=sp.id,
        drive_id=d.id,
        status="Applied",
        resume_path=resume_path,
    )
    db.session.add(app)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if save_path:
            try:
                os.remove(save_path)
            except OSError:
                pass
        return jsonify({"success": False, "error": "already_applied"}), 409
    except Exception:
        db.session.rollback()
        if save_path:
            try:
                os.remove(save_path)
            except OSError:
                pass
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_application_created(current_user.id, d.id)

    return jsonify({"success": True, "application_id": app.id, "status": app.status}), 201


@student_bp.route("/applications", methods=["GET"])
@student_required
@cache.cached(timeout=60, key_prefix=lambda: f"student:{current_user.id}:applications")
def list_applications():
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    apps = (
        Application.query
        .filter_by(student_profile_id=sp.id)
        .order_by(Application.application_date.desc())
        .all()
    )
    result = []
    for a in apps:
        d = a.drive
        cp = d.company_profile
        result.append({
            "application_id": a.id,
            "drive_id": d.id,
            "drive_status": d.status,
            "drive_available": (
                d.status == "Approved"
                and cp.approval_status == "Approved"
                and d.company_profile.user.is_active
            ),
            "company_name": cp.company_name,
            "job_title": d.job_title,
            "status": a.status,
            "offer_status": a.offer_status,
            "application_date": format_datetime(a.application_date),
            "resume_path": a.resume_path,
            "interview_datetime": format_datetime(a.interview_datetime),
            "interview_location": a.interview_location,
            "selection_date": format_datetime(a.selection_date),
            "remarks": a.remarks,
        })
    return jsonify({"success": True, "applications": result})


@student_bp.route("/applications/history", methods=["GET"])
@student_required
def placement_history():
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    now = datetime.now(timezone.utc)
    history_rows = (
        db.session.query(PlacementDrive, CompanyProfile, Application)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .outerjoin(
            Application,
            and_(
                Application.drive_id == PlacementDrive.id,
                Application.student_profile_id == sp.id,
            ),
        )
        .filter(
            or_(
                Application.id.isnot(None),
                and_(
                    PlacementDrive.application_deadline < now,
                    PlacementDrive.status.in_(("Approved", "Closed")),
                    CompanyProfile.approval_status == "Approved",
                ),
            )
        )
        .order_by(PlacementDrive.application_deadline.desc(), PlacementDrive.id.desc())
        .all()
    )
    result = []
    for d, cp, a in history_rows:
        status = a.status if a else (
            "Not Eligible" if check_eligibility(sp, d) else "Did Not Apply"
        )
        result.append({
            "application_id": a.id if a else None,
            "drive_id": d.id,
            "drive_status": d.status,
            "drive_available": (
                d.status == "Approved"
                and cp.approval_status == "Approved"
                and d.company_profile.user.is_active
                and _deadline_is_open(d.application_deadline, now)
            ),
            "company_name": cp.company_name,
            "job_title": d.job_title,
            "application_deadline": format_datetime(d.application_deadline),
            "application_date": format_datetime(a.application_date) if a else None,
            "status": status,
            "offer_status": a.offer_status if a else None,
            "selection_date": format_datetime(a.selection_date) if a else None,
            "remarks": a.remarks if a else None,
        })
    return jsonify({"success": True, "placement_history": result})


@student_bp.route("/applications/<int:application_id>/accept-offer", methods=["POST"])
@student_required
def accept_offer(application_id):
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    app = db.session.get(Application, application_id)
    if not app:
        return jsonify({"success": False, "error": "not_found"}), 404

    if app.student_profile_id != sp.id:
        return jsonify({"success": False, "error": "forbidden"}), 403

    if app.status != "Selected":
        return jsonify({"success": False, "error": "already_finalized"}), 409

    if app.offer_status != "Pending":
        return jsonify({"success": False, "error": "offer_not_pending"}), 409

    app.offer_status = "Accepted"

    Application.query.filter(
        Application.student_profile_id == sp.id,
        Application.status == "Selected",
        Application.offer_status == "Pending",
        Application.id != app.id,
    ).update({Application.offer_status: "Auto Declined"})

    drive_ids = [app.drive_id]
    other_apps = Application.query.filter(
        Application.student_profile_id == sp.id,
        Application.status == "Selected",
        Application.offer_status == "Auto Declined",
        Application.id != app.id,
    ).all()
    for other in other_apps:
        if other.drive_id not in drive_ids:
            drive_ids.append(other.drive_id)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_offer_status(sp.user_id, drive_ids)

    return jsonify({"success": True, "application_id": app.id, "offer_status": app.offer_status})


@student_bp.route("/applications/<int:application_id>/decline-offer", methods=["POST"])
@student_required
def decline_offer(application_id):
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    app = db.session.get(Application, application_id)
    if not app:
        return jsonify({"success": False, "error": "not_found"}), 404

    if app.student_profile_id != sp.id:
        return jsonify({"success": False, "error": "forbidden"}), 403

    if app.status != "Selected":
        return jsonify({"success": False, "error": "already_finalized"}), 409

    if app.offer_status != "Pending":
        return jsonify({"success": False, "error": "offer_not_pending"}), 409

    app.offer_status = "Declined"

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_offer_status(sp.user_id, [app.drive_id])

    return jsonify({"success": True, "application_id": app.id, "offer_status": app.offer_status})
