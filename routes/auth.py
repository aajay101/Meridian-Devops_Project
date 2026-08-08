from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from utils.constants import BRANCHES
from models import CompanyProfile, StudentProfile, User, db
from utils.cache_utils import (
    invalidate_admin_companies,
    invalidate_admin_dashboard,
    invalidate_admin_reports,
    invalidate_admin_students,
)
from utils.validators import (
    normalize_email,
    normalize_indian_phone_number,
    password_validation_error,
    validate_branch,
)

auth_bp = Blueprint("auth", __name__)

def _json_data():
    return request.get_json(silent=True) or {}


def _missing_fields(data, required_fields):
    return [field for field in required_fields if data.get(field) in (None, "")]


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


def _validate_hr_contact(hr_contact):
    if not hr_contact.isdigit() or len(hr_contact) != 10:
        return False
    return True


@auth_bp.route("/health")
def health():
    return jsonify({"status": "ok", "scope": "auth"})


@auth_bp.route("/branches", methods=["GET"])
def list_branches():
    return jsonify({"success": True, "branches": BRANCHES})


@auth_bp.route("/student/register", methods=["POST"])
def register_student():
    data = _json_data()
    required = ["name", "email", "password", "phone_number", "branch", "cgpa", "year"]
    missing = _missing_fields(data, required)
    if missing:
        return jsonify({"success": False, "error": "missing_fields", "fields": missing}), 400

    email = normalize_email(data["email"])
    if not email:
        return jsonify({"success": False, "error": "invalid_email_format"}), 400

    password_error = password_validation_error(data["password"])
    if password_error:
        return jsonify({"success": False, "error": password_error}), 400

    phone_number = normalize_indian_phone_number(data["phone_number"])
    if not phone_number:
        return jsonify({"success": False, "error": "invalid_phone_number"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "email_exists"}), 409
    if User.query.filter_by(phone_number=phone_number).first():
        return jsonify({"success": False, "error": "phone_number_exists"}), 409

    cgpa = _parse_float(data["cgpa"])
    if cgpa is None:
        return jsonify({"success": False, "error": "invalid_cgpa"}), 400
    if cgpa < 0.0 or cgpa > 10.0:
        return jsonify({"success": False, "error": "invalid_cgpa"}), 400

    year = _parse_int(data["year"])
    if year is None:
        return jsonify({"success": False, "error": "invalid_year"}), 400
    if year < 1:
        return jsonify({"success": False, "error": "invalid_year"}), 400

    errors = []
    _check_string(data, "name", 120, errors)
    _check_string(data, "email", 120, errors)
    if errors:
        return jsonify({"success": False, "error": "string_too_long", "details": errors}), 400

    if not validate_branch(data["branch"]):
        return jsonify({"success": False, "error": "invalid_branch"}), 400

    user = User(email=email, phone_number=phone_number, role="student")
    user.set_password(data["password"])
    profile = StudentProfile(
        user=user,
        name=data["name"],
        branch=data["branch"],
        cgpa=cgpa,
        year=year,
    )

    db.session.add(user)
    db.session.add(profile)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "error": "email_exists"}), 409
        return jsonify({"success": False, "error": "phone_number_exists"}), 409

    invalidate_admin_dashboard()
    invalidate_admin_students()
    invalidate_admin_reports()

    return jsonify({"success": True, "user_id": user.id, "role": user.role}), 201


@auth_bp.route("/company/register", methods=["POST"])
def register_company():
    data = _json_data()
    required = ["company_name", "email", "password", "phone_number", "hr_contact"]
    missing = _missing_fields(data, required)
    if missing:
        return jsonify({"success": False, "error": "missing_fields", "fields": missing}), 400

    email = normalize_email(data["email"])
    if not email:
        return jsonify({"success": False, "error": "invalid_email_format"}), 400

    password_error = password_validation_error(data["password"])
    if password_error:
        return jsonify({"success": False, "error": password_error}), 400

    phone_number = normalize_indian_phone_number(data["phone_number"])
    if not phone_number:
        return jsonify({"success": False, "error": "invalid_phone_number"}), 400

    if not _validate_hr_contact(data["hr_contact"]):
        return jsonify({"success": False, "error": "invalid_hr_contact"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "email_exists"}), 409
    if User.query.filter_by(phone_number=phone_number).first():
        return jsonify({"success": False, "error": "phone_number_exists"}), 409

    errors = []
    _check_string(data, "company_name", 120, errors)
    _check_string(data, "hr_contact", 120, errors)
    _check_string(data, "email", 120, errors)
    _check_string(data, "website", 255, errors)
    if errors:
        return jsonify({"success": False, "error": "string_too_long", "details": errors}), 400

    user = User(email=email, phone_number=phone_number, role="company")
    user.set_password(data["password"])
    profile = CompanyProfile(
        user=user,
        company_name=data["company_name"],
        hr_contact=data["hr_contact"],
        website=data.get("website"),
        approval_status="Pending",
    )

    db.session.add(user)
    db.session.add(profile)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "error": "email_exists"}), 409
        return jsonify({"success": False, "error": "phone_number_exists"}), 409

    invalidate_admin_dashboard()
    invalidate_admin_companies()
    invalidate_admin_reports()

    return jsonify({"success": True, "user_id": user.id, "role": user.role}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = _json_data()
    required = ["email", "password", "role"]
    missing = _missing_fields(data, required)
    if missing:
        return jsonify({"success": False, "error": "missing_fields", "fields": missing}), 400

    requested_role = data["role"].strip().lower()
    if requested_role not in ("student", "company", "admin"):
        return jsonify({"success": False, "error": "invalid_role"}), 400

    email = data["email"].strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"success": False, "error": "invalid_credentials"}), 401

    if not user.is_active:
        return jsonify({"success": False, "error": "account_disabled"}), 403

    if user.role == "company":
        cp = CompanyProfile.query.filter_by(user_id=user.id).first()
        if cp and cp.approval_status == "Rejected":
            return jsonify({"success": False, "error": "account_disabled"}), 403

    if requested_role != user.role:
        return jsonify({
            "success": False,
            "error": "role_mismatch",
            "message": "These credentials do not belong to the selected account type."
        }), 403

    login_user(user)
    return jsonify({"success": True, "user_id": user.id, "role": user.role})


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True})


@auth_bp.route("/me")
def me():
    if not current_user.is_authenticated:
        return jsonify({"authenticated": False})

    return jsonify(
        {
            "authenticated": True,
            "user_id": current_user.id,
            "role": current_user.role,
            "email": current_user.email,
            "phone_number": current_user.phone_number,
        }
    )
