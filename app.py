from flask import Flask, current_app, jsonify
from flask_login import LoginManager

from config import DevelopmentConfig
from models import User, db
from utils.cache_utils import init_cache

login_manager = LoginManager()
login_manager.login_view = "auth.login"


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


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    validate_production_config(app)

    db.init_app(app)
    login_manager.init_app(app)
    init_cache(app)

    register_error_handlers(app)
    register_blueprints(app)

    with app.app_context():
        db.create_all()
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
        "SECRET_KEY": "dev-secret-key",
        "ADMIN_PASSWORD": "admin123",
    }
    unsafe = [
        key for key, unsafe_value in unsafe_values.items()
        if app.config.get(key) == unsafe_value
    ]
    if unsafe:
        raise RuntimeError(f"Unsafe production config defaults: {', '.join(unsafe)}")


def register_blueprints(app):
    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.company import company_bp
    from routes.jobs import jobs_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(company_bp, url_prefix="/company")
    app.register_blueprint(jobs_bp, url_prefix="/jobs")
    app.register_blueprint(student_bp, url_prefix="/student")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


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


app = create_app()


@app.route("/health")
def health():
    return jsonify({"status": "ok", "scope": "app"})


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
