import os
import uuid

from flask import Blueprint, jsonify, request
from flask_login import current_user
from sqlalchemy import asc, or_

from models import Application, CompanyProfile, PlacementDrive, StudentProfile, db
from utils.validators import student_required

student_bp = Blueprint("student", __name__)


@student_bp.route("/health")
def health():
    return jsonify({"status": "ok", "scope": "student"})


@student_bp.route("/protected")
@student_required
def protected():
    return jsonify({"success": True, "scope": "student"})


def _get_student_profile():
    return current_user.student_profile


def _check_eligibility(sp, drive):
    violations = []
    if sp.branch != drive.eligibility_branch:
        violations.append("branch")
    if sp.cgpa < drive.eligibility_cgpa:
        violations.append("cgpa")
    if sp.year != drive.eligibility_year:
        violations.append("year")
    return violations


@student_bp.route("/profile", methods=["GET"])
@student_required
def get_profile():
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    return jsonify({
        "success": True,
        "user_id": sp.user_id,
        "name": sp.name,
        "email": sp.user.email,
        "branch": sp.branch,
        "cgpa": sp.cgpa,
        "year": sp.year,
        "resume_path": sp.resume_path,
        "created_at": sp.created_at.isoformat(),
    })


@student_bp.route("/profile", methods=["PUT"])
@student_required
def update_profile():
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    data = request.get_json(silent=True) or {}
    protected = {"user_id", "email", "role", "created_at"}
    errors = []

    if "cgpa" in data:
        try:
            cgpa = float(data["cgpa"])
            if cgpa < 0.0 or cgpa > 10.0:
                errors.append("cgpa must be between 0.0 and 10.0")
        except (TypeError, ValueError):
            errors.append("cgpa must be numeric")

    if "year" in data:
        raw = data["year"]
        if isinstance(raw, float) and not raw.is_integer():
            errors.append("year must be an integer")
        else:
            try:
                year = int(raw)
                if year < 1:
                    errors.append("year must be a positive integer")
            except (TypeError, ValueError):
                errors.append("year must be an integer")

    if errors:
        return jsonify({"success": False, "error": "validation_failed", "details": errors}), 400

    if "cgpa" in data:
        sp.cgpa = float(data["cgpa"])
    if "year" in data:
        sp.year = int(data["year"])
    if "name" in data:
        sp.name = data["name"]
    if "branch" in data:
        sp.branch = data["branch"]

    db.session.commit()

    return jsonify({
        "success": True,
        "user_id": sp.user_id,
        "name": sp.name,
        "email": sp.user.email,
        "branch": sp.branch,
        "cgpa": sp.cgpa,
        "year": sp.year,
        "created_at": sp.created_at.isoformat(),
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

    unique_name = f"{uuid.uuid4().hex}.pdf"
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads", "resumes")
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, unique_name)
    file.save(save_path)

    sp.resume_path = "uploads/resumes/" + unique_name
    db.session.commit()

    return jsonify({
        "success": True,
        "stored_filename": unique_name,
        "stored_path": sp.resume_path,
    }), 201


@student_bp.route("/drives", methods=["GET"])
@student_required
def list_drives():
    q = request.args.get("q", "").strip()
    query = (
        db.session.query(PlacementDrive, CompanyProfile)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .filter(PlacementDrive.status == "Approved")
    )
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                PlacementDrive.job_title.ilike(pattern),
                PlacementDrive.job_description.ilike(pattern),
                PlacementDrive.eligibility_branch.ilike(pattern),
                CompanyProfile.company_name.ilike(pattern),
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
            "eligibility_branch": d.eligibility_branch,
            "eligibility_cgpa": d.eligibility_cgpa,
            "eligibility_year": d.eligibility_year,
            "application_deadline": d.application_deadline.isoformat(),
            "created_at": d.created_at.isoformat(),
        })
    return jsonify({"success": True, "drives": result})


@student_bp.route("/drives/<int:drive_id>", methods=["GET"])
@student_required
def get_drive(drive_id):
    d = db.session.get(PlacementDrive, drive_id)
    if not d or d.status != "Approved":
        return jsonify({"success": False, "error": "not_found"}), 404

    cp = d.company_profile
    return jsonify({
        "success": True,
        "drive": {
            "drive_id": d.id,
            "company_name": cp.company_name,
            "job_title": d.job_title,
            "job_description": d.job_description,
            "eligibility_branch": d.eligibility_branch,
            "eligibility_cgpa": d.eligibility_cgpa,
            "eligibility_year": d.eligibility_year,
            "application_deadline": d.application_deadline.isoformat(),
            "created_at": d.created_at.isoformat(),
        },
    })


@student_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@student_required
def apply_to_drive(drive_id):
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    d = db.session.get(PlacementDrive, drive_id)
    if not d or d.status != "Approved":
        return jsonify({"success": False, "error": "drive_not_available"}), 403

    violations = _check_eligibility(sp, d)
    if violations:
        return jsonify({"success": False, "error": "ineligible", "violations": violations}), 403

    existing = Application.query.filter_by(
        student_profile_id=sp.id, drive_id=d.id
    ).first()
    if existing:
        return jsonify({"success": False, "error": "already_applied"}), 409

    app = Application(
        student_profile_id=sp.id,
        drive_id=d.id,
        status="Applied",
    )
    db.session.add(app)
    db.session.commit()

    return jsonify({"success": True, "application_id": app.id, "status": app.status}), 201


@student_bp.route("/applications", methods=["GET"])
@student_required
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
            "company_name": cp.company_name,
            "job_title": d.job_title,
            "status": a.status,
            "application_date": a.application_date.isoformat(),
        })
    return jsonify({"success": True, "applications": result})


@student_bp.route("/applications/history", methods=["GET"])
@student_required
def placement_history():
    sp = _get_student_profile()
    if not sp:
        return jsonify({"success": False, "error": "no_student_profile"}), 403

    apps = (
        Application.query
        .filter_by(student_profile_id=sp.id, status="Selected")
        .order_by(Application.selection_date.desc())
        .all()
    )
    result = []
    for a in apps:
        d = a.drive
        cp = d.company_profile
        result.append({
            "application_id": a.id,
            "drive_id": d.id,
            "company_name": cp.company_name,
            "job_title": d.job_title,
            "status": a.status,
            "selection_date": a.selection_date.isoformat() if a.selection_date else None,
            "remarks": a.remarks,
        })
    return jsonify({"success": True, "placement_history": result})
