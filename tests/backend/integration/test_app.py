
import pytest


def test_application_health(client):
    """Verify that the application health endpoint works."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "scope": "app",
    }


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/admin/protected",
        "/api/student/protected",
        "/api/company/protected",
    ],
)
def test_protected_endpoints_reject_unauthenticated_users(
    client,
    endpoint,
):
    """Verify that protected endpoints reject unauthenticated users."""

    response = client.get(endpoint)

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"
    assert response.get_json()["success"] is False
