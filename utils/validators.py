from functools import wraps

from flask import jsonify
from flask_login import current_user, login_required


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
