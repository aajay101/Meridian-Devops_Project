import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    _database_url = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = (
        _database_url
        if _database_url
        else f"sqlite:///{INSTANCE_DIR / 'placement.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # 127.0.0.1 avoids IPv6 (::1) double-timeout on Windows.
    # localhost resolves to [::1, 127.0.0.1]; Redis tries both sequentially.
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://127.0.0.1:6379/1")
    CACHE_TYPE = "utils.cache_utils.SafeRedisCache"
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))
    CACHE_OPTIONS = {"protocol": 2}
    # Seconds before SafeRedisCache attempts a recovery probe after failure.
    REDIS_FAILURE_COOLDOWN = int(os.getenv("REDIS_FAILURE_COOLDOWN", "30"))

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "Asia/Kolkata")

    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587") or 587)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@placement.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000")

    REMINDER_WINDOW_DAYS = int(os.getenv("REMINDER_WINDOW_DAYS", "3"))
    REMINDER_HOUR = int(os.getenv("REMINDER_HOUR", "8"))
    REMINDER_MINUTE = int(os.getenv("REMINDER_MINUTE", "0"))

    REPORT_HOUR = int(os.getenv("REPORT_HOUR", "6"))
    REPORT_MINUTE = int(os.getenv("REPORT_MINUTE", "0"))

    MAX_ACTIVE_OFFERS = int(os.getenv("MAX_ACTIVE_OFFERS", "3"))
    if MAX_ACTIVE_OFFERS < 1:
        MAX_ACTIVE_OFFERS = 3


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class TestConfig(BaseConfig):
    TESTING = True
    CACHE_TYPE = "SimpleCache"
    CACHE_OPTIONS = {}
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"
    SECRET_KEY = os.getenv("SECRET_KEY")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
