import json

from flask import Blueprint, jsonify, request
from sqlalchemy import asc, case, func, or_

from models import Application, CompanyProfile, PlacementDrive, StudentProfile, User, db
from utils.cache_utils import (
    cache,
    invalidate_admin_companies,
    invalidate_admin_students,
    invalidate_company_profile,
    invalidate_drive_status,
)
from utils.validators import admin_required

admin_bp = Blueprint("admin", __name__)


def _safe_json_loads(raw, default=None):
    if not raw:
        return default if default is not None else []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


def _get_student_with_user(student_profile_id):
    return (
        db.session.query(StudentProfile, User)
        .join(User, StudentProfile.user_id == User.id)
        .filter(StudentProfile.id == student_profile_id)
        .first()
    )


def _get_company_with_user(company_profile_id):
    return (
        db.session.query(CompanyProfile, User)
        .join(User, CompanyProfile.user_id == User.id)
        .filter(CompanyProfile.id == company_profile_id)
        .first()
    )


@admin_bp.route("/health")
def health():
    return jsonify({"status": "ok", "scope": "admin"})


@admin_bp.route("/protected")
@admin_required
def protected():
    return jsonify({"success": True, "scope": "admin"})


@admin_bp.route("/dashboard")
@admin_required
@cache.cached(timeout=120, key_prefix="admin:dashboard")
def dashboard():
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    return jsonify({
        "success": True,
        "total_students": total_students,
        "total_companies": total_companies,
        "total_drives": total_drives,
    })


@admin_bp.route("/reports/summary")
@admin_required
@cache.cached(timeout=300, key_prefix="admin:reports_summary")
def reports_summary():
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    applications_by_status = {"Applied": 0, "Shortlisted": 0, "Selected": 0, "Rejected": 0}
    if total_applications > 0:
        status_counts = (
            db.session.query(Application.status, func.count(Application.id))
            .group_by(Application.status)
            .all()
        )
        for status, count in status_counts:
            applications_by_status[status] = count

    selected_count = applications_by_status.get("Selected", 0)
    selection_rate = (selected_count / total_applications * 100) if total_applications > 0 else 0

    offer_status_counts = {"Accepted": 0, "Declined": 0, "Auto Declined": 0}
    if selected_count > 0:
        offer_counts = (
            db.session.query(Application.offer_status, func.count(Application.id))
            .filter(Application.status == "Selected", Application.offer_status.isnot(None))
            .group_by(Application.offer_status)
            .all()
        )
        for offer_status, count in offer_counts:
            if offer_status in offer_status_counts:
                offer_status_counts[offer_status] = count

    accepted_count = offer_status_counts.get("Accepted", 0)
    placement_rate = (accepted_count / total_applications * 100) if total_applications > 0 else 0

    return jsonify({
        "success": True,
        "total_students": total_students,
        "total_companies": total_companies,
        "total_drives": total_drives,
        "total_applications": total_applications,
        "applications_by_status": applications_by_status,
        "selection_rate": selection_rate,
        "offer_status_counts": offer_status_counts,
        "placement_rate": placement_rate,
    })


@admin_bp.route("/companies")
@admin_required
@cache.cached(timeout=300, key_prefix="admin:companies_list")
def list_companies():
    rows = (
        db.session.query(CompanyProfile, User)
        .join(User, CompanyProfile.user_id == User.id)
        .order_by(asc(CompanyProfile.created_at))
        .all()
    )
    companies = [
        {
            "company_profile_id": cp.id,
            "company_name": cp.company_name,
            "email": u.email,
            "hr_contact": cp.hr_contact,
            "approval_status": cp.approval_status,
            "is_active": u.is_active,
            "created_at": cp.created_at.isoformat(),
        }
        for cp, u in rows
    ]
    return jsonify({"success": True, "companies": companies})


@admin_bp.route("/companies/search")
@admin_required
def search_companies():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"success": True, "companies": []})

    pattern = f"%{q}%"
    rows = (
        db.session.query(CompanyProfile, User)
        .join(User, CompanyProfile.user_id == User.id)
        .filter(
            or_(
                CompanyProfile.company_name.ilike(pattern),
                User.email.ilike(pattern),
                CompanyProfile.hr_contact.ilike(pattern),
                CompanyProfile.approval_status.ilike(pattern),
            )
        )
        .order_by(asc(CompanyProfile.created_at))
        .all()
    )
    companies = [
        {
            "company_profile_id": cp.id,
            "company_name": cp.company_name,
            "email": u.email,
            "hr_contact": cp.hr_contact,
            "approval_status": cp.approval_status,
            "is_active": u.is_active,
            "created_at": cp.created_at.isoformat(),
        }
        for cp, u in rows
    ]
    return jsonify({"success": True, "companies": companies})


@admin_bp.route("/company/<int:company_profile_id>")
@admin_required
def get_company(company_profile_id):
    row = _get_company_with_user(company_profile_id)
    if not row:
        return jsonify({"success": False, "error": "not_found"}), 404

    cp, u = row
    return jsonify({
        "success": True,
        "company": {
            "company_profile_id": cp.id,
            "user_id": cp.user_id,
            "company_name": cp.company_name,
            "email": u.email,
            "hr_contact": cp.hr_contact,
            "website": cp.website,
            "approval_status": cp.approval_status,
            "is_active": u.is_active,
            "created_at": cp.created_at.isoformat(),
        },
    })


@admin_bp.route("/company/<int:company_profile_id>/deactivate", methods=["PATCH"])
@admin_required
def deactivate_company(company_profile_id):
    row = _get_company_with_user(company_profile_id)
    if not row:
        return jsonify({"success": False, "error": "not_found"}), 404

    cp, u = row
    if not u.is_active:
        return jsonify({"success": False, "error": "already_deactivated"}), 409

    u.is_active = False
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_admin_companies()

    return jsonify({
        "success": True,
        "company_profile_id": cp.id,
        "is_active": u.is_active,
    })


@admin_bp.route("/company/<int:company_profile_id>/activate", methods=["PATCH"])
@admin_required
def activate_company(company_profile_id):
    row = _get_company_with_user(company_profile_id)
    if not row:
        return jsonify({"success": False, "error": "not_found"}), 404

    cp, u = row
    if u.is_active:
        return jsonify({"success": False, "error": "already_active"}), 409

    u.is_active = True
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_admin_companies()

    return jsonify({
        "success": True,
        "company_profile_id": cp.id,
        "is_active": u.is_active,
    })


@admin_bp.route("/companies/pending")
@admin_required
@cache.cached(timeout=120, key_prefix="admin:companies_pending")
def list_pending_companies():
    rows = (
        db.session.query(CompanyProfile, User)
        .join(User, CompanyProfile.user_id == User.id)
        .filter(CompanyProfile.approval_status == "Pending")
        .order_by(asc(CompanyProfile.created_at))
        .all()
    )
    companies = [
        {
            "company_profile_id": cp.id,
            "company_name": cp.company_name,
            "email": u.email,
            "hr_contact": cp.hr_contact,
            "approval_status": cp.approval_status,
            "is_active": u.is_active,
            "created_at": cp.created_at.isoformat(),
        }
        for cp, u in rows
    ]
    return jsonify({"success": True, "companies": companies})


@admin_bp.route("/students")
@admin_required
@cache.cached(timeout=300, key_prefix="admin:students_list")
def list_students():
    rows = (
        db.session.query(StudentProfile, User)
        .join(User, StudentProfile.user_id == User.id)
        .order_by(asc(StudentProfile.created_at))
        .all()
    )
    students = [
        {
            "student_profile_id": sp.id,
            "user_id": sp.user_id,
            "name": sp.name,
            "email": u.email,
            "branch": sp.branch,
            "cgpa": sp.cgpa,
            "year": sp.year,
            "resume_path": sp.resume_path,
            "is_active": u.is_active,
            "created_at": sp.created_at.isoformat(),
        }
        for sp, u in rows
    ]
    return jsonify({"success": True, "students": students})


@admin_bp.route("/students/search")
@admin_required
def search_students():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"success": True, "students": []})

    pattern = f"%{q}%"
    status_expr = case(
        (User.is_active == True, "Active"),
        (User.is_active == False, "Inactive"),
    )
    rows = (
        db.session.query(StudentProfile, User)
        .join(User, StudentProfile.user_id == User.id)
        .filter(
            or_(
                StudentProfile.name.ilike(pattern),
                User.email.ilike(pattern),
                StudentProfile.branch.ilike(pattern),
                func.cast(StudentProfile.cgpa, db.String).ilike(pattern),
                StudentProfile.year.cast(db.String).ilike(pattern),
                status_expr.ilike(pattern),
            )
        )
        .order_by(asc(StudentProfile.created_at))
        .all()
    )
    students = [
        {
            "student_profile_id": sp.id,
            "user_id": sp.user_id,
            "name": sp.name,
            "email": u.email,
            "branch": sp.branch,
            "cgpa": sp.cgpa,
            "year": sp.year,
            "resume_path": sp.resume_path,
            "is_active": u.is_active,
            "created_at": sp.created_at.isoformat(),
        }
        for sp, u in rows
    ]
    return jsonify({"success": True, "students": students})


@admin_bp.route("/student/<int:student_profile_id>")
@admin_required
def get_student(student_profile_id):
    row = _get_student_with_user(student_profile_id)
    if not row:
        return jsonify({"success": False, "error": "not_found"}), 404

    sp, u = row
    return jsonify({
        "success": True,
        "student": {
            "student_profile_id": sp.id,
            "user_id": sp.user_id,
            "name": sp.name,
            "email": u.email,
            "branch": sp.branch,
            "cgpa": sp.cgpa,
            "year": sp.year,
            "resume_path": sp.resume_path,
            "is_active": u.is_active,
            "created_at": sp.created_at.isoformat(),
        },
    })


@admin_bp.route("/student/<int:student_profile_id>/deactivate", methods=["PATCH"])
@admin_required
def deactivate_student(student_profile_id):
    row = _get_student_with_user(student_profile_id)
    if not row:
        return jsonify({"success": False, "error": "not_found"}), 404

    sp, u = row
    if not u.is_active:
        return jsonify({"success": False, "error": "already_deactivated"}), 409

    u.is_active = False
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_admin_students()

    return jsonify({
        "success": True,
        "student_profile_id": sp.id,
        "is_active": u.is_active,
    })


@admin_bp.route("/student/<int:student_profile_id>/activate", methods=["PATCH"])
@admin_required
def activate_student(student_profile_id):
    row = _get_student_with_user(student_profile_id)
    if not row:
        return jsonify({"success": False, "error": "not_found"}), 404

    sp, u = row
    if u.is_active:
        return jsonify({"success": False, "error": "already_active"}), 409

    u.is_active = True
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_admin_students()

    return jsonify({
        "success": True,
        "student_profile_id": sp.id,
        "is_active": u.is_active,
    })


@admin_bp.route("/company/<int:company_profile_id>/approve", methods=["POST"])
@admin_required
def approve_company(company_profile_id):
    cp = db.session.get(CompanyProfile, company_profile_id)
    if not cp:
        return jsonify({"success": False, "error": "not_found"}), 404

    if cp.approval_status != "Pending":
        return jsonify({"success": False, "error": "already_finalized"}), 409

    cp.approval_status = "Approved"
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_admin_companies()
    invalidate_company_profile(cp.id)

    return jsonify({"success": True, "company_profile_id": cp.id, "approval_status": cp.approval_status})


@admin_bp.route("/company/<int:company_profile_id>/reject", methods=["POST"])
@admin_required
def reject_company(company_profile_id):
    cp = db.session.get(CompanyProfile, company_profile_id)
    if not cp:
        return jsonify({"success": False, "error": "not_found"}), 404

    if cp.approval_status != "Pending":
        return jsonify({"success": False, "error": "already_finalized"}), 409

    cp.approval_status = "Rejected"
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_admin_companies()
    invalidate_company_profile(cp.id)

    return jsonify({"success": True, "company_profile_id": cp.id, "approval_status": cp.approval_status})


@admin_bp.route("/drives")
@admin_required
@cache.cached(timeout=300, key_prefix="admin:drives_list")
def list_drives():
    rows = (
        db.session.query(PlacementDrive, CompanyProfile)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .order_by(asc(PlacementDrive.created_at))
        .all()
    )
    drives = [
        {
            "drive_id": d.id,
            "company_profile_id": d.company_profile_id,
            "company_name": cp.company_name,
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
        for d, cp in rows
    ]
    return jsonify({"success": True, "drives": drives})


@admin_bp.route("/drives/search")
@admin_required
def search_drives():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"success": True, "drives": []})

    pattern = f"%{q}%"
    rows = (
        db.session.query(PlacementDrive, CompanyProfile)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .filter(
            or_(
                PlacementDrive.job_title.ilike(pattern),
                CompanyProfile.company_name.ilike(pattern),
                PlacementDrive.eligibility_branches.ilike(pattern),
                PlacementDrive.eligibility_cgpa.cast(db.String).ilike(pattern),
                PlacementDrive.status.ilike(pattern),
            )
        )
        .order_by(asc(PlacementDrive.created_at))
        .all()
    )
    drives = [
        {
            "drive_id": d.id,
            "company_profile_id": d.company_profile_id,
            "company_name": cp.company_name,
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
        for d, cp in rows
    ]
    return jsonify({"success": True, "drives": drives})


@admin_bp.route("/drives/pending")
@admin_required
@cache.cached(timeout=120, key_prefix="admin:drives_pending")
def list_pending_drives():
    rows = (
        db.session.query(PlacementDrive, CompanyProfile)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .filter(PlacementDrive.status == "Pending")
        .order_by(asc(PlacementDrive.created_at))
        .all()
    )
    drives = [
        {
            "drive_id": d.id,
            "company_profile_id": d.company_profile_id,
            "company_name": cp.company_name,
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
        for d, cp in rows
    ]
    return jsonify({"success": True, "drives": drives})


@admin_bp.route("/drive/<int:drive_id>/approve", methods=["POST"])
@admin_required
def approve_drive(drive_id):
    d = db.session.get(PlacementDrive, drive_id)
    if not d:
        return jsonify({"success": False, "error": "not_found"}), 404
    if d.status != "Pending":
        return jsonify({"success": False, "error": "already_finalized"}), 409
    d.status = "Approved"
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_drive_status(d.company_profile_id, d.id)

    return jsonify({"success": True, "drive_id": d.id, "status": d.status})


@admin_bp.route("/drive/<int:drive_id>/reject", methods=["POST"])
@admin_required
def reject_drive(drive_id):
    d = db.session.get(PlacementDrive, drive_id)
    if not d:
        return jsonify({"success": False, "error": "not_found"}), 404
    if d.status != "Pending":
        return jsonify({"success": False, "error": "already_finalized"}), 409
    d.status = "Rejected"
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_drive_status(d.company_profile_id, d.id, include_shared=False)

    return jsonify({"success": True, "drive_id": d.id, "status": d.status})


@admin_bp.route("/drive/<int:drive_id>/close", methods=["POST"])
@admin_required
def close_drive(drive_id):
    d = db.session.get(PlacementDrive, drive_id)
    if not d:
        return jsonify({"success": False, "error": "not_found"}), 404
    if d.status != "Approved":
        return jsonify({"success": False, "error": "already_finalized"}), 409
    d.status = "Closed"
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "commit_failed"}), 500

    invalidate_drive_status(d.company_profile_id, d.id)
    return jsonify({"success": True, "drive_id": d.id, "status": d.status})


@admin_bp.route("/drives/approved")
@admin_required
def list_approved_drives():
    rows = (
        db.session.query(PlacementDrive, CompanyProfile)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .filter(PlacementDrive.status == "Approved")
        .order_by(asc(PlacementDrive.created_at))
        .all()
    )
    drives = [
        {
            "drive_id": d.id,
            "company_profile_id": d.company_profile_id,
            "company_name": cp.company_name,
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
        for d, cp in rows
    ]
    return jsonify({"success": True, "drives": drives})


@admin_bp.route("/drives/rejected")
@admin_required
def list_rejected_drives():
    rows = (
        db.session.query(PlacementDrive, CompanyProfile)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .filter(PlacementDrive.status == "Rejected")
        .order_by(asc(PlacementDrive.created_at))
        .all()
    )
    drives = [
        {
            "drive_id": d.id,
            "company_profile_id": d.company_profile_id,
            "company_name": cp.company_name,
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
        for d, cp in rows
    ]
    return jsonify({"success": True, "drives": drives})


@admin_bp.route("/drives/closed")
@admin_required
def list_closed_drives():
    rows = (
        db.session.query(PlacementDrive, CompanyProfile)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .filter(PlacementDrive.status == "Closed")
        .order_by(asc(PlacementDrive.created_at))
        .all()
    )
    drives = [
        {
            "drive_id": d.id,
            "company_profile_id": d.company_profile_id,
            "company_name": cp.company_name,
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
        for d, cp in rows
    ]
    return jsonify({"success": True, "drives": drives})


@admin_bp.route("/drive/<int:drive_id>")
@admin_required
def get_drive(drive_id):
    d = db.session.get(PlacementDrive, drive_id)
    if not d:
        return jsonify({"success": False, "error": "not_found"}), 404

    cp = d.company_profile
    return jsonify({
        "success": True,
        "drive": {
            "drive_id": d.id,
            "company_profile_id": d.company_profile_id,
            "company_name": cp.company_name,
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
        },
    })


@admin_bp.route("/applications")
@admin_required
@cache.cached(timeout=120, key_prefix="admin:applications_list")
def list_applications():
    apps = (
        db.session.query(Application, PlacementDrive, CompanyProfile)
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .order_by(Application.application_date.desc())
        .all()
    )
    result = []
    for a, d, cp in apps:
        sp = a.student_profile
        u = sp.user
        result.append({
            "application_id": a.id,
            "student_name": sp.name,
            "student_email": u.email,
            "branch": sp.branch,
            "cgpa": sp.cgpa,
            "company_name": cp.company_name,
            "job_title": d.job_title,
            "status": a.status,
            "offer_status": a.offer_status,
            "application_date": a.application_date.isoformat(),
            "resume_path": a.resume_path,
        })
    return jsonify({"success": True, "applications": result})


@admin_bp.route("/applications/search")
@admin_required
def search_applications():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"success": True, "applications": []})

    pattern = f"%{q}%"
    apps = (
        db.session.query(Application, PlacementDrive, CompanyProfile)
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .join(StudentProfile, Application.student_profile_id == StudentProfile.id)
        .join(User, StudentProfile.user_id == User.id)
        .filter(
            or_(
                StudentProfile.name.ilike(pattern),
                User.email.ilike(pattern),
                CompanyProfile.company_name.ilike(pattern),
                PlacementDrive.job_title.ilike(pattern),
                Application.status.ilike(pattern),
                Application.offer_status.ilike(pattern),
            )
        )
        .order_by(Application.application_date.desc())
        .all()
    )
    result = []
    for a, d, cp in apps:
        sp = a.student_profile
        u = sp.user
        result.append({
            "application_id": a.id,
            "student_name": sp.name,
            "student_email": u.email,
            "branch": sp.branch,
            "cgpa": sp.cgpa,
            "company_name": cp.company_name,
            "job_title": d.job_title,
            "status": a.status,
            "offer_status": a.offer_status,
            "application_date": a.application_date.isoformat(),
            "resume_path": a.resume_path,
        })
    return jsonify({"success": True, "applications": result})
