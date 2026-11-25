
import hmac
import logging
import os

from flask import (
    Flask,
    current_app,
    jsonify,
    request,
    send_from_directory,
    session,
)
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from werkzeug.utils import safe_join

from config import (
    DevelopmentConfig,
    ProductionConfig,
    TestConfig,
    get_database_url,
)
from models import User, db
from utils.cache_utils import init_cache


logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Authentication and application extensions
# ---------------------------------------------------------

login_manager = LoginManager()
login_manager.login_view = "api.auth.login"

migrate = Migrate()


@login_manager.unauthorized_handler
def unauthorized():

    return jsonify({
        "success": False,
        "error": "unauthorized",
    }), 401


def register_error_handlers(app):

    @app.errorhandler(403)
    def forbidden(e):

        return jsonify({
            "success": False,
            "error": "forbidden",
        }), 403

    @app.errorhandler(404)
    def not_found(e):

        return jsonify({
            "success": False,
            "error": "not_found",
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):

        return jsonify({
            "success": False,
            "error": "method_not_allowed",
        }), 405

    @app.errorhandler(500)
    def internal_error(e):

        return jsonify({
            "success": False,
            "error": "internal_server_error",
        }), 500


# ---------------------------------------------------------
# Application routes
# ---------------------------------------------------------

def health():

    return jsonify({
        "status": "ok",
        "scope": "app",
    })


def serve_resume(filename):

    if not filename:

        return jsonify({
            "success": False,
            "error": "not_found",
        }), 404

    if not current_user.is_authenticated:

        return jsonify({
            "success": False,
            "error": "unauthorized",
        }), 401

    requested_path = os.path.join(
        "uploads",
        "resumes",
        filename,
    ).replace(os.sep, "/")

    authorized = current_user.role == "admin"

    from models import Application, PlacementDrive

    linked_application = Application.query.filter_by(
        resume_path=requested_path
    ).first()

    if current_user.role == "student" and current_user.student_profile:

        profile = current_user.student_profile

        linked_application = Application.query.filter_by(
            resume_path=requested_path,
            student_profile_id=profile.id,
        ).first()

        authorized = (
            profile.resume_path == requested_path
            or linked_application is not None
        )

    elif current_user.role == "company" and current_user.company_profile:

        linked_application = (
            db.session.query(Application)
            .join(
                PlacementDrive,
                Application.drive_id == PlacementDrive.id,
            )
            .filter(
                Application.resume_path == requested_path,
                PlacementDrive.company_profile_id
                == current_user.company_profile.id,
            )
            .first()
        )

        authorized = linked_application is not None

    if not authorized:

        return jsonify({
            "success": False,
            "error": "forbidden",
        }), 403

    upload_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "uploads",
        "resumes",
    )

    safe_path = safe_join(upload_dir, filename)

    if (
        safe_path is None or not os.path.isfile(safe_path)
    ) and linked_application:

        fallback = linked_application.student_profile.resume_path or ""
        prefix = "uploads/resumes/"

        if fallback.startswith(prefix):

            fallback_filename = fallback[len(prefix):]
            fallback_path = safe_join(upload_dir, fallback_filename)

            if fallback_path and os.path.isfile(fallback_path):

                filename = fallback_filename
                safe_path = fallback_path

    if safe_path is None or not os.path.isfile(safe_path):

        return jsonify({
            "success": False,
            "error": "not_found",
        }), 404

    return send_from_directory(
        upload_dir,
        filename,
        mimetype="application/pdf",
    )


# ---------------------------------------------------------
# Flask application factory
# ---------------------------------------------------------

def create_app(config_class=None):

    if config_class is None:

        environment = os.getenv(
            "APP_ENV",
            os.getenv("FLASK_ENV", "development"),
        ).lower()

        if environment == "testing":
            config_class = TestConfig

        elif environment == "production":
            config_class = ProductionConfig

        else:
            config_class = DevelopmentConfig

    app = Flask(__name__)

    # Load the selected application configuration.
    app.config.from_object(config_class)

    # Resolve only the database belonging to the selected
    # environment. Other database credentials are not needed.
    database_environment = getattr(
        config_class,
        "DATABASE_ENV",
        None,
    )

    if not database_environment:

        raise RuntimeError(
            "Selected configuration does not define DATABASE_ENV."
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url(
        database_environment
    )

    # Validate production-specific security settings.
    validate_production_config(app)

    # Initialize extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    init_cache(app)

    # Register application components.
    register_error_handlers(app)
    register_blueprints(app)

    app.add_url_rule(
        "/health",
        endpoint="health",
        view_func=health,
    )

    app.add_url_rule(
        "/uploads/resumes/<path:filename>",
        endpoint="serve_resume",
        view_func=serve_resume,
    )

    @app.before_request
    def protect_state_changing_requests():

        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return None

        if request.path in {
            "/api/auth/login",
            "/api/auth/student/register",
            "/api/auth/company/register",
        }:
            return None

        if not current_user.is_authenticated:
            return None

        expected = session.get("csrf_token")
        supplied = request.headers.get("X-CSRF-Token", "")

        if (
            not expected
            or not supplied
            or not hmac.compare_digest(expected, supplied)
        ):

            return jsonify({
                "success": False,
                "error": "csrf_failed",
            }), 403

        return None

    @app.after_request
    def expose_csrf_token(response):

        token = session.get("csrf_token")

        if token:
            response.headers["X-CSRF-Token"] = token

        return response

    # Administrator creation is an explicit CLI operation.
    @app.cli.command("seed-admin")
    def seed_admin_command():

        """Create the default administrator if one does not exist."""

        with app.app_context():
            seed_default_admin()

        print("Administrator seed operation completed.")

    # Database schema is managed through Flask-Migrate.
    # Do not call db.create_all() here.

    return app


# ---------------------------------------------------------
# Production configuration validation
# ---------------------------------------------------------

def validate_production_config(app):

    if app.config.get("ENV") != "production":
        return

    required = [
        "SECRET_KEY",
        "ADMIN_PASSWORD",
    ]

    missing = [
        key for key in required
        if not app.config.get(key)
    ]

    if missing:

        raise RuntimeError(
            f"Missing required production config: {', '.join(missing)}"
        )

    unsafe_values = {
        "SECRET_KEY": {
            "dev-secret-key",
            "change-me",
            "change-this-secret-key",
            "your-secret-key",
        },
        "ADMIN_PASSWORD": "admin123",
    }

    def is_unsafe(key, value):

        unsafe_value = unsafe_values[key]

        if isinstance(unsafe_value, set):
            return value in unsafe_value

        return value == unsafe_value

    unsafe = [
        key
        for key in unsafe_values
        if is_unsafe(key, app.config.get(key))
    ]

    if unsafe:

        raise RuntimeError(
            f"Unsafe production config defaults: {', '.join(unsafe)}"
        )


# ---------------------------------------------------------
# Blueprint registration
# ---------------------------------------------------------

def register_blueprints(app):

    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.company import company_bp
    from routes.jobs import jobs_bp
    from routes.student import student_bp

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth",
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/api/admin",
    )

    app.register_blueprint(
        company_bp,
        url_prefix="/api/company",
    )

    app.register_blueprint(
        jobs_bp,
        url_prefix="/api/jobs",
    )

    app.register_blueprint(
        student_bp,
        url_prefix="/api/student",
    )


# ---------------------------------------------------------
# Flask-Login user loader
# ---------------------------------------------------------

@login_manager.user_loader
def load_user(user_id):

    try:
        user = db.session.get(User, int(user_id))

    except (TypeError, ValueError):
        return None

    if user and not user.is_active:
        return None

    return user


# ---------------------------------------------------------
# Default administrator seeding
# ---------------------------------------------------------

def seed_default_admin():

    email = current_app.config["ADMIN_EMAIL"]
    password = current_app.config.get("ADMIN_PASSWORD")

    if not password:

        raise RuntimeError(
            "ADMIN_PASSWORD must be configured before seeding the admin."
        )

    existing_admin = User.query.filter_by(
        role="admin"
    ).first()

    if existing_admin:

        logger.info("An administrator account already exists.")
        return

    admin = User(
        email=email,
        role="admin",
    )

    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    logger.info("Default administrator created successfully.")


# ---------------------------------------------------------
# Application entry point
# ---------------------------------------------------------

app = create_app()


if __name__ == "__main__":

    # Bind to 0.0.0.0 so the Flask process is reachable
    # from outside its Docker container.
    #
    # PostgreSQL is managed independently by Docker Compose.

    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    logger.info(
        "Starting Meridian Flask development server on %s:%s",
        host,
        port,
    )

    app.run(
        host=host,
        port=port,
        debug=app.config.get("DEBUG", False),
        use_reloader=False,
    )
