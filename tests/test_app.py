import copy
from urllib.parse import quote

import pytest

from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Make a deep copy of activities before each test and restore after so tests don't leak state."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # should be a dict containing activity names
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister(client):
    activity = "Chess Club"
    email = "testuser@example.com"

    # make sure email is not already present
    assert email not in activities[activity]["participants"]

    # Signup
    activity_encoded = quote(activity, safe="")
    signup_resp = client.post(f"/activities/{activity_encoded}/signup?email={email}")
    assert signup_resp.status_code == 200
    assert f"Signed up {email}" in signup_resp.json()["message"]

    # Check participant was added
    get_resp = client.get("/activities")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert email in data[activity]["participants"]

    # Unregister
    unregister_resp = client.delete(f"/activities/{activity_encoded}/unregister?email={email}")
    assert unregister_resp.status_code == 200
    assert f"Unregistered {email}" in unregister_resp.json()["message"]

    # Ensure removed
    get_resp2 = client.get("/activities")
    data2 = get_resp2.json()
    assert email not in data2[activity]["participants"]
