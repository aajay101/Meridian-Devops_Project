
import sys
from pathlib import Path

import pytest


# Add the backend directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = PROJECT_ROOT / "src" / "backend"

sys.path.insert(0, str(BACKEND_PATH))


from app import create_app
from config import TestConfig
from models import db


@pytest.fixture(scope="session")
def app():
    """Create the Flask application using the test configuration."""

    test_app = create_app(TestConfig)

    database_uri = str(
        test_app.config["SQLALCHEMY_DATABASE_URI"]
    )

    if not database_uri.endswith("/meridian_test"):
        raise RuntimeError(
            "Safety check failed: tests must use meridian_test."
        )

    if not test_app.config.get("TESTING"):
        raise RuntimeError(
            "Safety check failed: Flask testing mode is disabled."
        )

    yield test_app


@pytest.fixture()
def client(app):
    """Provide a Flask test client."""

    return app.test_client()


@pytest.fixture()
def app_context(app):
    """Provide an application context for database operations."""

    with app.app_context():
        yield

        db.session.remove()
