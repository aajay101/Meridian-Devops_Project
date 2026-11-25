
import os

from sqlalchemy.engine import URL

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------
# Environment variable helpers
# ---------------------------------------------------------

def get_bool_env(name, default="false"):
    """Convert an environment variable into a boolean."""

    return os.getenv(name, default).strip().lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


def get_int_env(name, default):
    """Read an integer environment variable safely."""

    try:
        return int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise RuntimeError(
            f"{name} must be a valid integer."
        ) from exc


# ---------------------------------------------------------
# PostgreSQL configuration
# ---------------------------------------------------------

def get_database_url(environment):
    """Build a PostgreSQL URL for the selected environment only."""

    prefix = environment.upper()

    required = [
        f"{prefix}_DB_NAME",
        f"{prefix}_DB_USER",
        f"{prefix}_DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
    ]

    missing = [
        key for key in required
        if not os.getenv(key)
    ]

    if missing:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing)
        )

    try:
        port = int(os.getenv("DB_PORT"))
    except ValueError as exc:
        raise RuntimeError(
            "DB_PORT must be a valid integer."
        ) from exc

    return URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv(f"{prefix}_DB_USER"),
        password=os.getenv(f"{prefix}_DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=port,
        database=os.getenv(f"{prefix}_DB_NAME"),
    )


# ---------------------------------------------------------
# Base application configuration
# ---------------------------------------------------------

class BaseConfig:

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # -----------------------------------------------------
    # Session and cookie configuration
    # -----------------------------------------------------

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = get_bool_env(
        "SESSION_COOKIE_SECURE",
        "false",
    )

    # -----------------------------------------------------
    # Redis configuration
    # -----------------------------------------------------

    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0",
    )

    CACHE_REDIS_URL = os.getenv(
        "CACHE_REDIS_URL",
        "redis://localhost:6379/1",
    )

    CACHE_TYPE = "utils.cache_utils.SafeRedisCache"

    CACHE_DEFAULT_TIMEOUT = get_int_env(
        "CACHE_DEFAULT_TIMEOUT",
        300,
    )

    CACHE_OPTIONS = {
        "protocol": 2,
    }

    REDIS_FAILURE_COOLDOWN = get_int_env(
        "REDIS_FAILURE_COOLDOWN",
        30,
    )

    # -----------------------------------------------------
    # Celery configuration
    # -----------------------------------------------------

    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL",
        REDIS_URL,
    )

    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND",
        REDIS_URL,
    )

    CELERY_TIMEZONE = os.getenv(
        "CELERY_TIMEZONE",
        "Asia/Kolkata",
    )

    # -----------------------------------------------------
    # Email configuration
    # -----------------------------------------------------

    MAIL_SERVER = os.getenv(
        "MAIL_SERVER",
        "",
    )

    MAIL_PORT = get_int_env(
        "MAIL_PORT",
        587,
    )

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME",
        "",
    )

    MAIL_PASSWORD = os.getenv(
        "MAIL_PASSWORD",
        "",
    )

    MAIL_USE_TLS = get_bool_env(
        "MAIL_USE_TLS",
        "true",
    )

    # -----------------------------------------------------
    # Administrator configuration
    # -----------------------------------------------------

    ADMIN_EMAIL = os.getenv(
        "ADMIN_EMAIL",
        "admin@placement.local",
    )

    ADMIN_PASSWORD = os.getenv(
        "ADMIN_PASSWORD",
    )

    # -----------------------------------------------------
    # Application URL configuration
    # -----------------------------------------------------

    APP_BASE_URL = os.getenv(
        "APP_BASE_URL",
        "http://127.0.0.1:8000",
    )

    # -----------------------------------------------------
    # Placement reminder configuration
    # -----------------------------------------------------

    REMINDER_WINDOW_DAYS = get_int_env(
        "REMINDER_WINDOW_DAYS",
        3,
    )

    REMINDER_HOUR = get_int_env(
        "REMINDER_HOUR",
        8,
    )

    REMINDER_MINUTE = get_int_env(
        "REMINDER_MINUTE",
        0,
    )

    # -----------------------------------------------------
    # Monthly report configuration
    # -----------------------------------------------------

    REPORT_HOUR = get_int_env(
        "REPORT_HOUR",
        6,
    )

    REPORT_MINUTE = get_int_env(
        "REPORT_MINUTE",
        0,
    )

    # -----------------------------------------------------
    # Placement business rules
    # -----------------------------------------------------

    MAX_ACTIVE_OFFERS = get_int_env(
        "MAX_ACTIVE_OFFERS",
        3,
    )

    if MAX_ACTIVE_OFFERS < 1:
        MAX_ACTIVE_OFFERS = 3


# ---------------------------------------------------------
# Development configuration
# ---------------------------------------------------------

class DevelopmentConfig(BaseConfig):

    DEBUG = True
    ENV = "development"

    DATABASE_ENV = "DEV"


# ---------------------------------------------------------
# Testing configuration
# ---------------------------------------------------------

class TestConfig(BaseConfig):

    TESTING = True
    ENV = "testing"

    # Tests do not depend on Redis.
    CACHE_TYPE = "SimpleCache"
    CACHE_OPTIONS = {}

    DATABASE_ENV = "TEST"


# ---------------------------------------------------------
# Production configuration
# ---------------------------------------------------------

class ProductionConfig(BaseConfig):

    DEBUG = False
    ENV = "production"

    SESSION_COOKIE_SECURE = True

    DATABASE_ENV = "PROD"
