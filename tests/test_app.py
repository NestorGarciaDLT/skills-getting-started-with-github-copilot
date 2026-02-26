import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test."""
    original = {
        name: {**data, "participants": list(data["participants"])}
        for name, data in activities.items()
    }
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


def test_signup_for_activity():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in response.json()["message"]


def test_signup_activity_not_found():
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"},
    )
    assert response.status_code == 404


def test_signup_duplicate_participant():
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "duplicate@mergington.edu"},
    )
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "duplicate@mergington.edu"},
    )
    assert response.status_code == 400


def test_unregister_from_activity():
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "todelete@mergington.edu"},
    )
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "todelete@mergington.edu"},
    )
    assert response.status_code == 200
    assert "todelete@mergington.edu" in response.json()["message"]


def test_unregister_not_registered():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "notregistered@mergington.edu"},
    )
    assert response.status_code == 404


def test_unregister_activity_not_found():
    response = client.delete(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"},
    )
    assert response.status_code == 404
