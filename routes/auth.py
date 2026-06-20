from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from models import CompanyProfile, StudentProfile, User, db

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


@auth_bp.route("/health")
def health():
    return jsonify({"status": "ok", "scope": "auth"})


@auth_bp.route("/student/register", methods=["POST"])
def register_student():
    data = _json_data()
    required = ["name", "email", "password", "branch", "cgpa", "year"]
    missing = _missing_fields(data, required)
    if missing:
        return jsonify({"success": False, "error": "missing_fields", "fields": missing}), 400

    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "email_exists"}), 409

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
    _check_string(data, "branch", 80, errors)
    _check_string(data, "email", 120, errors)
    if errors:
        return jsonify({"success": False, "error": "string_too_long", "details": errors}), 400

    user = User(email=email, role="student")
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
    db.session.commit()

    return jsonify({"success": True, "user_id": user.id, "role": user.role}), 201


@auth_bp.route("/company/register", methods=["POST"])
def register_company():
    data = _json_data()
    required = ["company_name", "email", "password", "hr_contact"]
    missing = _missing_fields(data, required)
    if missing:
        return jsonify({"success": False, "error": "missing_fields", "fields": missing}), 400

    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "email_exists"}), 409

    errors = []
    _check_string(data, "company_name", 120, errors)
    _check_string(data, "hr_contact", 120, errors)
    _check_string(data, "email", 120, errors)
    _check_string(data, "website", 255, errors)
    if errors:
        return jsonify({"success": False, "error": "string_too_long", "details": errors}), 400

    user = User(email=email, role="company")
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
    db.session.commit()

    return jsonify({"success": True, "user_id": user.id, "role": user.role}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = _json_data()
    required = ["email", "password"]
    missing = _missing_fields(data, required)
    if missing:
        return jsonify({"success": False, "error": "missing_fields", "fields": missing}), 400

    email = data["email"].strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"success": False, "error": "invalid_credentials"}), 401

    if not user.is_active:
        return jsonify({"success": False, "error": "account_disabled"}), 403

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
        }
    ) 
