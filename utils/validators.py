import json
import re
from functools import wraps

from flask import jsonify
from flask_login import current_user, login_required

from constants import BRANCH_SET

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def is_valid_email(email):
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email))


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

    if len(branches) != len(set(branches)):
        return False

    for branch in branches:
        if not isinstance(branch, str) or branch not in BRANCH_SET:
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
