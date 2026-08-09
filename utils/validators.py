import json
import re
from datetime import timezone
from functools import wraps
from urllib.parse import urlsplit

from flask import jsonify
from flask_login import current_user, login_required

from utils.constants import BRANCH_SET

EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)
PHONE_REGEX = re.compile(r"^[6-9]\d{9}$")

def normalize_email(email):
    """Return a canonical email address, or None when it is invalid."""
    if not isinstance(email, str):
        return None
    normalized = email.strip().lower()
    if not normalized or len(normalized) > 120 or any(char.isspace() for char in normalized):
        return None
    return normalized if EMAIL_REGEX.fullmatch(normalized) else None


def escape_like(value):
    """Escape SQL LIKE metacharacters for literal substring searches."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def format_datetime(value):
    """Serialize database datetimes as explicit UTC ISO-8601 values."""
    if value is None:
        return None
    normalized = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    return normalized.isoformat().replace("+00:00", "Z")


def is_valid_email(email):
    return normalize_email(email) is not None


def is_safe_website(value):
    """Allow only absolute HTTP(S) URLs for links rendered by the UI."""
    if value in (None, ""):
        return True
    if not isinstance(value, str) or len(value) > 255:
        return False
    parsed = urlsplit(value.strip())
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


def normalize_indian_phone_number(phone_number):
    """Normalize supported Indian mobile forms to a 10-digit canonical value."""
    if not isinstance(phone_number, str):
        return None
    value = phone_number.strip()
    if not value:
        return None
    if re.fullmatch(r"\d{10}", value):
        normalized = value
    elif re.fullmatch(r"\+91 \d{10}", value) or re.fullmatch(r"\+91\d{10}", value):
        normalized = value[-10:]
    else:
        return None
    return normalized if PHONE_REGEX.fullmatch(normalized) else None


def password_validation_error(password):
    """Return the API error code for an invalid new password, else None."""
    if not isinstance(password, str):
        return "invalid_password"
    if len(password) < 8:
        return "password_too_short"
    if len(password) > 12:
        return "password_too_long"
    if any(char.isspace() for char in password):
        return "password_contains_whitespace"
    if not re.search(r"[a-z]", password):
        return "password_missing_lowercase"
    if not re.search(r"[A-Z]", password):
        return "password_missing_uppercase"
    if not re.search(r"\d", password):
        return "password_missing_number"
    if not re.search(r"[^A-Za-z0-9\s]", password):
        return "password_missing_special"
    return None


def validate_branch(branch):
    if not branch or not isinstance(branch, str):
        return False
    return branch in BRANCH_SET


def validate_branches(branches):
    """Validate a list of branch names.

    Args:
        branches: List of branch name strings

    Returns:
        True if valid, False otherwise

    Validation rules:
        - Input must be a list
        - List cannot be empty
        - No duplicates allowed
        - Every value must exist in BRANCHES
    """
    if not isinstance(branches, list):
        return False

    if len(branches) == 0:
        return False

    for branch in branches:
        if not isinstance(branch, str) or branch not in BRANCH_SET:
            return False

    if len(branches) != len(set(branches)):
        return False

    return True


def get_eligible_branches(drive):
    """Get the list of eligible branches from a drive.

    Args:
        drive: PlacementDrive model instance

    Returns:
        List of branch name strings
    """
    try:
        return json.loads(drive.eligibility_branches)
    except (json.JSONDecodeError, TypeError, AttributeError):
        return []


def check_eligibility(student_profile, drive):
    violations = []

    eligible_branches = get_eligible_branches(drive)
    if student_profile.branch not in eligible_branches:
        violations.append("branch")

    if student_profile.cgpa < drive.eligibility_cgpa:
        violations.append("cgpa")

    if drive.eligibility_year_mode == "minimum":
        if student_profile.year < drive.eligibility_year:
            violations.append("year")
    else:
        if student_profile.year != drive.eligibility_year:
            violations.append("year")

    return violations


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role != role:
                return jsonify({"success": False, "error": "forbidden"}), 403
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


admin_required = role_required("admin")
company_required = role_required("company")
student_required = role_required("student")
