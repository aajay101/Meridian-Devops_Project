import json
import logging
import hmac
import os
import sqlite3

from flask import Flask, current_app, jsonify, request, send_from_directory, session
from flask_login import LoginManager, current_user
from werkzeug.utils import safe_join

from config import DevelopmentConfig, ProductionConfig
from utils.constants import BRANCH_MIGRATION_MAP
from models import User, db
from utils.cache_utils import init_cache

logger = logging.getLogger(__name__)

login_manager = LoginManager()
login_manager.login_view = "api.auth.login"


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"success": False, "error": "unauthorized"}), 401


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "error": "forbidden"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "not_found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "method_not_allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "internal_server_error"}), 500


def health():
    return jsonify({"status": "ok", "scope": "app"})


def serve_resume(filename):
    if not filename:
        return jsonify({"success": False, "error": "not_found"}), 404

    if not current_user.is_authenticated:
        return jsonify({"success": False, "error": "unauthorized"}), 401

    requested_path = os.path.join("uploads", "resumes", filename).replace(os.sep, "/")
    authorized = current_user.role == "admin"

    from models import Application, PlacementDrive

    linked_application = Application.query.filter_by(resume_path=requested_path).first()

    if current_user.role == "student" and current_user.student_profile:
        profile = current_user.student_profile
        linked_application = Application.query.filter_by(
            resume_path=requested_path,
            student_profile_id=profile.id,
        ).first()
        authorized = profile.resume_path == requested_path or linked_application is not None
    elif current_user.role == "company" and current_user.company_profile:
        linked_application = (
            db.session.query(Application)
            .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
            .filter(
                Application.resume_path == requested_path,
                PlacementDrive.company_profile_id == current_user.company_profile.id,
            )
            .first()
        )
        authorized = (
            linked_application is not None
        )

    if not authorized:
        return jsonify({"success": False, "error": "forbidden"}), 403

    upload_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "uploads", "resumes"
    )

    safe_path = safe_join(upload_dir, filename)
    if (safe_path is None or not os.path.isfile(safe_path)) and linked_application:
        fallback = linked_application.student_profile.resume_path or ""
        prefix = "uploads/resumes/"
        if fallback.startswith(prefix):
            fallback_filename = fallback[len(prefix):]
            fallback_path = safe_join(upload_dir, fallback_filename)
            if fallback_path and os.path.isfile(fallback_path):
                filename = fallback_filename
                safe_path = fallback_path
    if safe_path is None or not os.path.isfile(safe_path):
        return jsonify({"success": False, "error": "not_found"}), 404

    return send_from_directory(upload_dir, filename, mimetype="application/pdf")


def create_app(config_class=None):
    if config_class is None:
        environment = os.getenv("APP_ENV", os.getenv("FLASK_ENV", "development")).lower()
        config_class = ProductionConfig if environment == "production" else DevelopmentConfig

    app = Flask(__name__)
    app.config.from_object(config_class)
    validate_production_config(app)

    db.init_app(app)
    login_manager.init_app(app)
    init_cache(app)

    register_error_handlers(app)
    register_blueprints(app)
    app.add_url_rule("/health", endpoint="health", view_func=health)
    app.add_url_rule(
        "/uploads/resumes/<path:filename>",
        endpoint="serve_resume",
        view_func=serve_resume,
    )

    @app.before_request
    def protect_state_changing_requests():
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return None
        if request.path in {"/api/auth/login", "/api/auth/student/register", "/api/auth/company/register"}:
            return None
        if not current_user.is_authenticated:
            return None

        expected = session.get("csrf_token")
        supplied = request.headers.get("X-CSRF-Token", "")
        if not expected or not supplied or not hmac.compare_digest(supplied, expected):
            return jsonify({"success": False, "error": "csrf_failed"}), 403
        return None

    @app.after_request
    def expose_csrf_token(response):
        token = session.get("csrf_token")
        if token:
            response.headers["X-CSRF-Token"] = token
        return response

    with app.app_context():
        db.create_all()
        migrate_existing_db()
        seed_default_admin()

    return app


def validate_production_config(app):
    if app.config.get("ENV") != "production":
        return

    required = ["SECRET_KEY", "ADMIN_PASSWORD"]
    missing = [key for key in required if not app.config.get(key)]
    if missing:
        raise RuntimeError(f"Missing required production config: {', '.join(missing)}")

    unsafe_values = {
        "SECRET_KEY": {"dev-secret-key", "change-me", "change-this-secret-key", "your-secret-key"},
        "ADMIN_PASSWORD": "admin123",
    }

    def is_unsafe(key, value):
        unsafe_value = unsafe_values[key]
        return value in unsafe_value if isinstance(unsafe_value, set) else value == unsafe_value

    unsafe = [
        key for key, unsafe_value in unsafe_values.items()
        if is_unsafe(key, app.config.get(key))
    ]
    if unsafe:
        raise RuntimeError(f"Unsafe production config defaults: {', '.join(unsafe)}")


def register_blueprints(app):
    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.company import company_bp
    from routes.jobs import jobs_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(company_bp, url_prefix="/api/company")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(student_bp, url_prefix="/api/student")


@login_manager.user_loader
def load_user(user_id):
    try:
        user = db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
    if user and not user.is_active:
        return None
    return user


def seed_default_admin():
    email = current_app.config["ADMIN_EMAIL"]
    password = current_app.config["ADMIN_PASSWORD"]

    if User.query.filter_by(role="admin").first():
        return

    admin = User(
        email=email,
        role="admin",
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()


def migrate_existing_db():
    """Add missing columns to existing tables."""
    uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not uri.startswith("sqlite:///"):
        return

    db_path = uri.replace("sqlite:///", "")
    if not db_path or db_path == ":memory:":
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(placement_drive)")
        columns = [col[1] for col in cursor.fetchall()]

        if "eligibility_year_mode" not in columns:
            cursor.execute(
                "ALTER TABLE placement_drive ADD COLUMN eligibility_year_mode VARCHAR(10) DEFAULT 'exact'"
            )
            conn.commit()

        if "eligibility_branches" not in columns:
            cursor.execute(
                "ALTER TABLE placement_drive ADD COLUMN eligibility_branches TEXT NOT NULL DEFAULT '[]'"
            )
            conn.commit()
            logger.info("Added eligibility_branches column to placement_drive table")

        cursor.execute("PRAGMA table_info(user)")
        user_columns = [col[1] for col in cursor.fetchall()]
        if "phone_number" not in user_columns:
            cursor.execute("ALTER TABLE user ADD COLUMN phone_number VARCHAR(10)")
            conn.commit()
            logger.info("Added phone_number column to user table")

        cursor.execute(
            "SELECT phone_number FROM user WHERE phone_number IS NOT NULL "
            "GROUP BY phone_number HAVING COUNT(*) > 1"
        )
        duplicate_phone_numbers = cursor.fetchall()
        if duplicate_phone_numbers:
            logger.error("Cannot create unique user phone_number index; duplicate values exist")
        else:
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_user_phone_number "
                "ON user(phone_number) WHERE phone_number IS NOT NULL"
            )
            conn.commit()

        cursor.execute("PRAGMA table_info(application)")
        app_columns = [col[1] for col in cursor.fetchall()]

        if "resume_path" not in app_columns:
            cursor.execute(
                "ALTER TABLE application ADD COLUMN resume_path VARCHAR(255)"
            )
            conn.commit()

        if "offer_status" not in app_columns:
            cursor.execute(
                "ALTER TABLE application ADD COLUMN offer_status VARCHAR(20)"
            )
            conn.commit()

        _migrate_branch_values(cursor, conn)
        _migrate_branches_to_json(cursor, conn)

        conn.close()
    except Exception:
        logger.exception("Database migration failed")


def _migrate_branch_values(cursor, conn):
    """Migrate legacy branch values to standardized format."""
    for table, column in [("student_profile", "branch"), ("placement_drive", "eligibility_branch")]:
        try:
            cursor.execute(f"SELECT DISTINCT {column} FROM {table}")
            values = [row[0] for row in cursor.fetchall() if row[0]]
            for old_value in values:
                new_value = BRANCH_MIGRATION_MAP.get(old_value)
                if new_value and new_value != old_value:
                    cursor.execute(
                        f"UPDATE {table} SET {column} = ? WHERE {column} = ?",
                        (new_value, old_value),
                    )
            conn.commit()
        except Exception:
            logger.warning("Failed to migrate branch values for %s.%s", table, column)


def _migrate_branches_to_json(cursor, conn):
    """Migrate eligibility_branch to eligibility_branches JSON array."""
    try:
        cursor.execute(
            "SELECT id, eligibility_branch FROM placement_drive WHERE eligibility_branches = '[]' OR eligibility_branches IS NULL"
        )
        drives = cursor.fetchall()
        migrated_count = 0
        for drive_id, eligibility_branch in drives:
            if eligibility_branch:
                branches_json = json.dumps([eligibility_branch])
                cursor.execute(
                    "UPDATE placement_drive SET eligibility_branches = ? WHERE id = ?",
                    (branches_json, drive_id),
                )
                migrated_count += 1
        if migrated_count > 0:
            conn.commit()
            logger.info("Migrated %d drives from eligibility_branch to eligibility_branches", migrated_count)
    except Exception:
        logger.exception("Failed to migrate eligibility_branches")


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
